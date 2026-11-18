from __future__ import annotations

import logging
import os
import signal
import threading
import time

from sqlalchemy import inspect

from db.queries import crawl_jobs
from db.session import SessionLocal

from .jobs import HANDLERS
from .pacing import TokenBucket
from .providers.deezer import DeezerClient

DEFAULT_RPS = 4.0
EMPTY_LANE_SLEEP = 2.0

log = logging.getLogger("crawler.runtime")

_stop = threading.Event()


def deezer_rps() -> float:
    return float(os.environ.get("DEEZER_RPS", DEFAULT_RPS))


def make_client() -> DeezerClient:
    return DeezerClient(TokenBucket(deezer_rps()))


def install_signal_handlers() -> threading.Event:
    """Ask the lane loop to stop after the job in flight. Returns the stop flag."""

    def handle(signum, frame):
        log.info("signal %s received, finishing current job", signum)
        _stop.set()

    signal.signal(signal.SIGINT, handle)
    # SIGTERM is what the container gets on Linux; it never fires on Windows.
    signal.signal(signal.SIGTERM, handle)
    return _stop


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s"
    )


def _hand_back(db, job_id, record, *args) -> None:
    """Drop the handler's half-finished work, then record the job's new state.

    Without the rollback a failed statement would poison the session, so
    recording the outcome would fail too and leave the job stuck in `running`.
    An interrupt mid-handler would otherwise commit a partial write alongside
    the requeue. A failure to record is logged, never raised, so it cannot mask
    the error that brought us here.
    """
    try:
        db.rollback()
        record(db, job_id, *args)
    except Exception:
        log.exception("could not record outcome for job id=%s", job_id)
        try:
            db.rollback()
        except Exception:
            log.exception("session unusable, lane will stop on job id=%s", job_id)


def run_lane(lane: str, *, drain: bool, max_artists: int) -> None:
    """Claim and run jobs in one lane until it empties (drain) or we are stopped."""
    db = SessionLocal()
    client = make_client()
    try:
        while not _stop.is_set():
            job = crawl_jobs.claim(db, lane)
            if job is None:
                if drain:
                    return
                time.sleep(EMPTY_LANE_SLEEP)
                continue

            # claim() commits, which expires every attribute. Reading the identity
            # map issues no SQL, so this cannot fail before _hand_back can run.
            job_id = inspect(job).identity[0]
            try:
                kind, target, payload = job.kind, job.target, job.payload
                log.info(
                    "claimed job id=%s target=%s pid=%s", job_id, target, os.getpid()
                )
                handler = HANDLERS.get(kind)
                if handler is None:
                    raise ValueError(f"unknown job kind {kind!r}")
                handler(db, client, target, payload, max_artists=max_artists)
                crawl_jobs.complete(db, job_id)
            except Exception as exc:  # one bad job must not stop the lane
                log.exception("job id=%s failed", job_id)
                _hand_back(db, job_id, crawl_jobs.fail, str(exc))
            except BaseException:
                _hand_back(db, job_id, crawl_jobs.release)
                raise
    finally:
        db.close()
