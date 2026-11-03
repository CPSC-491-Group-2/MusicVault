"""The fixed recommendation dataset, as in-memory rows or loaded into a database.

Shared by test_recommendation_regression.py (in memory, no database) and
test_recommendation_inputs.py (real database). Both give every artist and
song the same UUID on every run, so their rankings can be compared with the
same snapshot.
"""

from __future__ import annotations

import json
import math
import uuid
from pathlib import Path

from sqlalchemy.orm import Session

from models.artist import Artist, SongArtist
from models.song import Song
from models.user import User
from models.user_top_song import UserTopSong

DATA_DIR = Path(__file__).parent / "data"
DATASET_FILE = DATA_DIR / "recommendation_dataset.json"
SNAPSHOT_FILE = DATA_DIR / "recommendation_expected.json"

DATASET = json.loads(DATASET_FILE.read_text())
PROFILES = {key: p["seeds"] for key, p in DATASET["profiles"].items()}

# Fixed namespace, so every run gives each dataset entry the same UUID.
NAMESPACE = uuid.UUID("6f1c2a3e-0000-4000-8000-000000000491")


def stable_id(kind, key):
    return uuid.uuid5(NAMESPACE, f"{kind}:{key}")


KEY_BY_TRACK_ID = {str(stable_id("song", key)): key for key in DATASET["songs"]}


def snapshot(recommendations):
    """A ranking as plain JSON data; scores rounded to keep the file stable."""
    return [
        {
            "song": KEY_BY_TRACK_ID[r.track_id],
            "score": round(r.score, 6),
            "reason": r.reason,
            "components": {
                name: None if value is None else round(value, 6)
                for name, value in r.components.items()
            },
        }
        for r in recommendations
    ]


def build_songs(audio=lambda values: values):
    """Song and Artist rows for the dataset, keyed by song key; not saved.

    `audio` transforms each song's audio features before they're set.
    """
    artists = {
        key: Artist(id=stable_id("artist", key), name=a["name"], genres=a["genres"])
        for key, a in DATASET["artists"].items()
    }
    songs = {}
    for key, s in DATASET["songs"].items():
        song = Song(
            id=stable_id("song", key),
            title=key,
            artist_name=", ".join(artists[a].name for a in s["artists"]),
            audio_features=audio(s["audio"]),
            popularity=s["popularity"],
        )
        song.artist_credits = [
            SongArtist(artist=artists[a], position=position)
            for position, a in enumerate(s["artists"], start=1)
        ]
        songs[key] = song
    return songs


def json_safe(audio):
    """Replace NaN and infinities, which JSONB can't store, with null.

    The scorer ignores those values anyway, so this doesn't change any
    song's features.
    """
    if audio is None:
        return None
    return {
        name: None if isinstance(v, float) and not math.isfinite(v) else v
        for name, v in audio.items()
    }


def load_into_database(db: Session, time_range="medium_term"):
    """Save the dataset, plus one user per profile with its seeds as top songs.

    Commits, so use it with clean_database. Returns {profile: user_id}.
    """
    db.add_all(build_songs(audio=json_safe).values())
    users = {}
    for profile, seeds in PROFILES.items():
        user = User(id=stable_id("user", profile), display_name=profile)
        db.add(user)
        users[profile] = user.id
        db.add_all(
            UserTopSong(
                user_id=user.id,
                song_id=stable_id("song", key),
                time_range=time_range,
                rank=rank,
            )
            for rank, key in enumerate(seeds, start=1)
        )
    db.commit()
    return users
