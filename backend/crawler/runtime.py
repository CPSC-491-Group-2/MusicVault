from __future__ import annotations

import logging
import os
import signal
import threading
import time

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

            # claim() commits, so these attributes expire and would re-query later.
            job_id, kind, target, payload = job.id, job.kind, job.target, job.payload
            log.info("claimed job id=%s target=%s pid=%s", job_id, target, os.getpid())
            try:
                handler = HANDLERS.get(kind)
                if handler is None:
                    raise ValueError(f"unknown job kind {kind!r}")
                handler(db, client, target, payload, max_artists=max_artists)
            except Exception as exc:  # one bad job must not stop the lane
                log.exception("job id=%s failed", job_id)
                crawl_jobs.fail(db, job_id, str(exc))
            except BaseException:
                crawl_jobs.release(db, job_id)
                raise
            else:
                crawl_jobs.complete(db, job_id)
    finally:
        db.close()
