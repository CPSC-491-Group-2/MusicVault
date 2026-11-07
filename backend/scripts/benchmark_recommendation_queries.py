"""Time the recommendation queries on generated catalogs of several sizes.

Records the performance baseline in docs/recommendation-data-integrity.md.
Everything it writes happens inside one transaction that is rolled back at
the end, so the database is left exactly as it was.

Runs against TEST_DATABASE_URL, which must name a database ending in
"_test" whose schema already exists (running the test suite once creates
it). From the backend directory:

    PYTHONPATH=.:../spotify-api-backend python scripts/benchmark_recommendation_queries.py
"""

from __future__ import annotations

import os
import statistics
import sys
import time
import uuid

from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from app.services.similarity import rank_candidates, track_features_from_song
from db.queries.preferences import save_preferences, set_preference
from db.queries.recommendations import get_recommendation_inputs
from models.artist import Artist, SongArtist
from models.song import Song
from models.user import User
from models.user_top_song import UserTopSong

CATALOG_SIZES = (1_000, 5_000, 20_000)
TOP_SONGS = 50
PREFERENCES = 20
RUNS = 5


def main() -> None:
    url = os.environ.get(
        "TEST_DATABASE_URL", "postgresql+psycopg2://localhost:5432/musicvault_test"
    )
    if not (make_url(url).database or "").endswith("_test"):
        sys.exit("TEST_DATABASE_URL must name a database ending in '_test'")

    engine = create_engine(url)
    print(f"{RUNS} runs each; median (min-max) in ms\n")
    print(
        "| Songs | Load inputs | Build features | Rank | Total "
        "| Set 1 preference | Save 20 preferences |"
    )
    print("|---|---|---|---|---|---|---|")
    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            db = Session(bind=connection, join_transaction_mode="create_savepoint")
            added = 0
            user_id = None
            for size in CATALOG_SIZES:
                songs = add_songs(db, size - added)
                added = size
                if user_id is None:
                    user_id = add_user(db, songs)
                print(benchmark(db, user_id, size))
        finally:
            transaction.rollback()
    engine.dispose()


def add_songs(db: Session, count: int) -> list[Song]:
    artists = [
        Artist(name=f"Bench artist {uuid.uuid4()}", genres=["pop", f"genre {n % 25}"])
        for n in range(count // 4 + 1)
    ]
    songs = []
    for n in range(count):
        song = Song(
            title=f"Bench song {n}",
            artist_name="",
            popularity=n % 100,
            audio_features={
                "energy": n % 10 / 10,
                "danceability": n % 7 / 7,
                "valence": n % 5 / 5,
                "acousticness": n % 3 / 3,
                "tempo": 80 + n % 80,
            },
        )
        song.artist_credits = [
            SongArtist(artist=artists[n % len(artists)], position=1),
            SongArtist(artist=artists[(n + 1) % len(artists)], position=2),
        ]
        songs.append(song)
    db.add_all(songs)
    db.commit()
    return songs


def add_user(db: Session, songs: list[Song]) -> uuid.UUID:
    user = User(display_name="Benchmark")
    db.add(user)
    db.flush()
    db.add_all(
        UserTopSong(user_id=user.id, song_id=song.id, time_range="medium_term", rank=r)
        for r, song in enumerate(songs[:TOP_SONGS], start=1)
    )
    db.commit()
    save_preferences(
        db,
        user.id,
        [
            {"song_id": song.id, "preference_type": "liked", "rating": 4}
            for song in songs[TOP_SONGS : TOP_SONGS + PREFERENCES]
        ],
    )
    return user.id


def benchmark(db: Session, user_id: uuid.UUID, size: int) -> str:
    load, build, rank, total = [], [], [], []
    for _ in range(RUNS):
        db.expunge_all()  # time real loads, not the session's identity map
        start = time.perf_counter()
        inputs = get_recommendation_inputs(db, user_id)
        loaded = time.perf_counter()
        seeds = [track_features_from_song(s) for s in inputs.seeds]
        candidates = [track_features_from_song(s) for s in inputs.candidates]
        built = time.perf_counter()
        rank_candidates(seeds, candidates, limit=50)
        ranked = time.perf_counter()
        load.append(loaded - start)
        build.append(built - loaded)
        rank.append(ranked - built)
        total.append(ranked - start)

    song_ids = [s.id for s in inputs.candidates[:PREFERENCES]]
    # Commits walk every object the session holds; drop the loaded catalog
    # so the write timings measure the database, not the session.
    del inputs, seeds, candidates
    db.expunge_all()
    one = timed(lambda: set_preference(db, user_id, song_ids[0], "saved"))
    batch = timed(
        lambda: save_preferences(
            db,
            user_id,
            [{"song_id": s, "preference_type": "neutral"} for s in song_ids],
        )
    )
    cells = [fmt(t) for t in (load, build, rank, total, one, batch)]
    return f"| {size:,} | " + " | ".join(cells) + " |"


def timed(action) -> list[float]:
    times = []
    for _ in range(RUNS):
        start = time.perf_counter()
        action()
        times.append(time.perf_counter() - start)
    return times


def fmt(times: list[float]) -> str:
    ms = [t * 1000 for t in times]
    return f"{statistics.median(ms):.1f} ({min(ms):.1f}-{max(ms):.1f})"


if __name__ == "__main__":
    main()
