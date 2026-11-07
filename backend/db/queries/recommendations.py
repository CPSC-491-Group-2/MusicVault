from __future__ import annotations

import uuid
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from models.artist import SongArtist
from models.song import Song
from models.user_preference import UserPreference
from models.user_top_song import TIME_RANGES, UserTopSong

# Preferences that make a song a seed, and ones that keep it out entirely.
SEED_PREFERENCES = ("liked", "saved")
EXCLUDED_PREFERENCES = ("disliked", "skipped")


@dataclass(frozen=True)
class RecommendationInputs:
    """What the ranker needs for one user, with artists and genres loaded.

    `seeds` are the user's songs, best first; `candidates` are every other
    song that could be recommended, in a fixed order (by song ID).
    """

    seeds: list[Song]
    candidates: list[Song]


def get_recommendation_inputs(
    db: Session, user_id: uuid.UUID, time_range: str = "medium_term"
) -> RecommendationInputs:
    """Load a user's seed songs and the candidate songs to rank against them.

    Seeds are the user's top songs for `time_range` in rank order, followed
    by songs they liked or saved (highest rating first). Candidates are all
    other songs. Songs the user disliked or skipped are in neither list.

    Each song's artist credits and artists are loaded up front, so building
    TrackFeatures afterwards runs no more queries. The number of queries
    doesn't grow with the number of songs.
    """
    if time_range not in TIME_RANGES:
        raise ValueError(
            f"time_range must be one of {', '.join(TIME_RANGES)} (got {time_range!r})"
        )

    excluded = (
        select(UserPreference.song_id)
        .where(
            UserPreference.user_id == user_id,
            UserPreference.preference_type.in_(EXCLUDED_PREFERENCES),
        )
        .scalar_subquery()
    )
    with_artists = selectinload(Song.artist_credits).selectinload(SongArtist.artist)

    top_songs = db.scalars(
        select(Song)
        .join(UserTopSong, UserTopSong.song_id == Song.id)
        .where(
            UserTopSong.user_id == user_id,
            UserTopSong.time_range == time_range,
            Song.id.not_in(excluded),
        )
        .order_by(UserTopSong.rank)
        .options(with_artists)
    ).all()
    preferred = db.scalars(
        select(Song)
        .join(UserPreference, UserPreference.song_id == Song.id)
        .where(
            UserPreference.user_id == user_id,
            UserPreference.preference_type.in_(SEED_PREFERENCES),
        )
        .order_by(
            UserPreference.rating.desc().nulls_last(),
            UserPreference.created_at,
            Song.id,
        )
        .options(with_artists)
    ).all()

    seeds, seed_ids = [], set()
    for song in [*top_songs, *preferred]:
        if song.id not in seed_ids:
            seed_ids.add(song.id)
            seeds.append(song)

    candidate_query = select(Song).where(Song.id.not_in(excluded))
    if seed_ids:
        candidate_query = candidate_query.where(Song.id.not_in(seed_ids))
    candidates = db.scalars(
        candidate_query.order_by(Song.id).options(with_artists)
    ).all()

    return RecommendationInputs(seeds=list(seeds), candidates=list(candidates))
