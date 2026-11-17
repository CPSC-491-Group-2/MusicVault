from __future__ import annotations

import uuid
from datetime import timedelta

from sqlalchemy import and_, func, or_, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from models.crawl_job import CrawlJob

PRIORITY_ON_DEMAND = 100
PRIORITY_SEED = 50
PRIORITY_REFRESH = 10
MAX_ATTEMPTS = 5


def enqueue(
    db: Session,
    *,
    kind: str,
    lane: str,
    target: str,
    payload: dict | None = None,
    priority: int = PRIORITY_SEED,
    requeue_age: timedelta = timedelta(days=1),
) -> uuid.UUID | None:
    """Queue one job per (kind, target) and return its id, or None if it is live.

    A job already queued or running is left alone, so re-seeding the same
    target is cheap. A `failed` job is retried immediately, and a `done` job
    only once `requeue_age` has passed since it finished. Re-queuing keeps the
    higher of the two priorities: an on-demand job stays ahead of the seed
    crawl even if the seeder asks for it again.
    """
    statement = insert(CrawlJob).values(
        kind=kind, lane=lane, target=target, payload=payload, priority=priority
    )
    upsert = statement.on_conflict_do_update(
        constraint="uq_crawl_jobs_kind_target",
        set_={
            "status": "queued",
            "attempts": 0,
            "run_after": func.now(),
            "last_error": None,
            "payload": statement.excluded.payload,
            "priority": func.greatest(CrawlJob.priority, statement.excluded.priority),
            "updated_at": func.now(),
        },
        where=or_(
            CrawlJob.status == "failed",
            and_(
                CrawlJob.status == "done",
                CrawlJob.updated_at <= func.now() - requeue_age,
            ),
        ),
    ).returning(CrawlJob.id)

    try:
        job_id = db.scalar(upsert)
        db.commit()
    except Exception:
        db.rollback()
        raise
    return job_id


def claim(db: Session, lane: str) -> CrawlJob | None:
    """Take the next due job in a lane, or None when the lane has none ready.

    The row is locked with SKIP LOCKED, so several workers on the same lane
    never claim the same job. This is the only place `attempts` grows.
    """
    try:
        job = db.scalar(
            select(CrawlJob)
            .where(
                CrawlJob.lane == lane,
                CrawlJob.status == "queued",
                CrawlJob.run_after <= func.now(),
            )
            .order_by(CrawlJob.priority.desc(), CrawlJob.run_after)
            .limit(1)
            .with_for_update(skip_locked=True)
        )
        if job is not None:
            job.status = "running"
            job.attempts = job.attempts + 1
            job.updated_at = func.now()
        db.commit()
    except Exception:
        db.rollback()
        raise
    return job


def complete(db: Session, job_id: uuid.UUID) -> None:
    db.execute(
        update(CrawlJob)
        .where(CrawlJob.id == job_id)
        .values(status="done", last_error=None, updated_at=func.now())
    )
    db.commit()


def fail(db: Session, job_id: uuid.UUID, error: str) -> None:
    """Record a failed run, retrying with exponential backoff until MAX_ATTEMPTS."""
    job = db.get(CrawlJob, job_id, with_for_update=True)
    if job is None:
        raise ValueError(f"no crawl job with id {job_id!r}")

    try:
        job.last_error = error[:1000]
        job.updated_at = func.now()
        if job.attempts >= MAX_ATTEMPTS:
            job.status = "failed"
        else:
            job.status = "queued"
            job.run_after = func.now() + timedelta(minutes=2**job.attempts)
        db.commit()
    except Exception:
        db.rollback()
        raise


def release(db: Session, job_id: uuid.UUID) -> None:
    """Hand a claimed job back to the queue, keeping the attempt claim() counted."""
    db.execute(
        update(CrawlJob)
        .where(CrawlJob.id == job_id)
        .values(status="queued", run_after=func.now(), updated_at=func.now())
    )
    db.commit()


def status_counts(db: Session) -> list[tuple[str, str, int]]:
    rows = db.execute(
        select(CrawlJob.lane, CrawlJob.status, func.count())
        .group_by(CrawlJob.lane, CrawlJob.status)
        .order_by(CrawlJob.lane, CrawlJob.status)
    ).all()
    return [(lane, status, count) for lane, status, count in rows]


def oldest_queued_age(db: Session) -> timedelta | None:
    """How long the longest-waiting queued job has existed, or None if idle."""
    return db.scalar(
        select(func.now() - func.min(CrawlJob.created_at)).where(
            CrawlJob.status == "queued"
        )
    )
