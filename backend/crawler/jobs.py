from __future__ import annotations

import logging
from datetime import timedelta

from sqlalchemy.orm import Session

from db.queries import catalog, crawl_jobs

from .providers.deezer import DeezerClient

KIND_EXPAND_ARTIST = "expand_artist"
LANE_DEEZER = "deezer"
RELATED_LIMIT = 20
TOP_TRACKS_LIMIT = 25

log = logging.getLogger("crawler.jobs")


def expand_artist(
    db: Session,
    client: DeezerClient,
    target: str,
    payload: dict | None,
    *,
    max_artists: int,
) -> None:
    """Import one Deezer artist with its related artists and top tracks.

    Related artists are weighted by their position in Deezer's own ordering,
    so the first one scores 1.0. With a remaining `depth` in the payload, each
    related artist is queued for its own expansion, but only while the catalog
    is still under `max_artists` — the frontier grows twentyfold per level, so
    the cap is re-checked before every enqueue.
    """
    src_id = catalog.upsert_artist_from_deezer(db, client.artist(target))

    related = client.related_artists(target, limit=RELATED_LIMIT)
    for i, dst in enumerate(related):
        dst_id = catalog.upsert_artist_from_deezer(db, dst)
        if dst_id == src_id:
            continue
        catalog.upsert_edge(
            db,
            src_artist_id=src_id,
            dst_artist_id=dst_id,
            provider="deezer_related",
            weight=1 - i / len(related),
        )

    for track in client.top_tracks(target, limit=TOP_TRACKS_LIMIT):
        catalog.upsert_song_from_deezer(db, track)

    depth = (payload or {}).get("depth") or 0
    if depth > 0:
        for dst in related:
            if catalog.catalog_counts(db)["artists"] >= max_artists:
                log.info("artist cap %s reached, not expanding further", max_artists)
                break
            crawl_jobs.enqueue(
                db,
                kind=KIND_EXPAND_ARTIST,
                lane=LANE_DEEZER,
                target=dst["deezer_id"],
                payload={"depth": depth - 1},
                priority=crawl_jobs.PRIORITY_SEED,
                requeue_age=timedelta(days=1),
            )

    catalog.mark_expanded(db, src_id)


HANDLERS = {KIND_EXPAND_ARTIST: expand_artist}
