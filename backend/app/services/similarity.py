"""Similarity scoring between songs, and ranking candidates for a user.

Everything here is a pure function of its inputs: no database access, no
clock, no randomness. The same songs and config always give the same scores
in the same order. See docs/similarity-scoring.md for the formulas, the
default weights and why they were chosen.

Each component (artist, genre, audio) scores a pair of songs from 0 to 1, or
returns None when either song lacks that data. The overall score averages
only the components that have data, so a song with no genres or audio
features is still scored on its artists alone.
"""

from __future__ import annotations

import math
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.song import Song

ALGORITHM_VERSION = "similarity-v1"

COMPONENTS = ("artist", "genre", "audio")

# Audio features compared by default, and the difference between two songs
# that counts as completely dissimilar. Features Spotify-style providers
# report on a 0-1 scale use 1.0; tempo is in BPM.
DEFAULT_AUDIO_FEATURE_RANGES = MappingProxyType(
    {
        "danceability": 1.0,
        "energy": 1.0,
        "valence": 1.0,
        "acousticness": 1.0,
        "tempo": 60.0,
    }
)


@dataclass(frozen=True)
class TrackFeatures:
    """What the scorer knows about one song.

    `track_id` is any stable identifier; it breaks ties in rankings. Empty
    `artists`/`genres` and an empty `audio` mean "unknown", not "none".
    """

    track_id: str
    artists: frozenset[str] = frozenset()
    genres: frozenset[str] = frozenset()
    audio: Mapping[str, float] = field(default_factory=dict)
    popularity: int | None = None


@dataclass(frozen=True)
class ScoringConfig:
    """Tunable parameters. The defaults are documented baselines.

    Component weights are relative: only their ratios matter, and they are
    rescaled over the components that have data for a given pair.
    """

    artist_weight: float = 0.35
    genre_weight: float = 0.35
    audio_weight: float = 0.30
    # Seed i (0 = the user's top song) counts seed_rank_decay ** i.
    seed_rank_decay: float = 0.9
    # Scales a candidate's score by (1 - popularity_penalty * popularity / 100),
    # to favour lesser-known songs. Off by default.
    popularity_penalty: float = 0.0
    audio_feature_ranges: Mapping[str, float] = DEFAULT_AUDIO_FEATURE_RANGES

    def __post_init__(self):
        weights = self.weights()
        if any(w < 0 for w in weights.values()):
            raise ValueError("component weights must not be negative")
        if sum(weights.values()) <= 0:
            raise ValueError("at least one component weight must be positive")
        if not 0 < self.seed_rank_decay <= 1:
            raise ValueError("seed_rank_decay must be in (0, 1]")
        if not 0 <= self.popularity_penalty <= 1:
            raise ValueError("popularity_penalty must be in [0, 1]")
        if any(r <= 0 for r in self.audio_feature_ranges.values()):
            raise ValueError("audio feature ranges must be positive")

    def weights(self) -> dict[str, float]:
        return {
            "artist": self.artist_weight,
            "genre": self.genre_weight,
            "audio": self.audio_weight,
        }


DEFAULT_CONFIG = ScoringConfig()


@dataclass(frozen=True)
class Similarity:
    score: float
    components: dict[str, float | None]


@dataclass(frozen=True)
class Recommendation:
    """A ranked candidate. `reason` is the component that contributed most."""

    track_id: str
    score: float
    reason: str | None
    components: dict[str, float | None]


def overlap(a: frozenset[str], b: frozenset[str]) -> float | None:
    """Jaccard similarity: shared items / all items. None if either is empty."""
    if not a or not b:
        return None
    return len(a & b) / len(a | b)


def artist_similarity(a: TrackFeatures, b: TrackFeatures) -> float | None:
    return overlap(a.artists, b.artists)


def genre_similarity(a: TrackFeatures, b: TrackFeatures) -> float | None:
    return overlap(a.genres, b.genres)


def audio_similarity(
    a: TrackFeatures,
    b: TrackFeatures,
    feature_ranges: Mapping[str, float] = DEFAULT_AUDIO_FEATURE_RANGES,
) -> float | None:
    """1 minus the mean scaled difference over features both songs have.

    Each difference is divided by that feature's range and capped at 1, so a
    tempo gap of 60 BPM or more counts as completely different.
    """
    distances = [
        min(abs(a.audio[name] - b.audio[name]) / scale, 1.0)
        for name, scale in sorted(feature_ranges.items())
        if _is_number(a.audio.get(name)) and _is_number(b.audio.get(name))
    ]
    if not distances:
        return None
    return 1.0 - sum(distances) / len(distances)


def similarity(
    a: TrackFeatures, b: TrackFeatures, config: ScoringConfig = DEFAULT_CONFIG
) -> Similarity:
    """Weighted mean of the components that have data for both songs.

    The score is 0 when no component has data.
    """
    components = {
        "artist": artist_similarity(a, b),
        "genre": genre_similarity(a, b),
        "audio": audio_similarity(a, b, config.audio_feature_ranges),
    }
    return Similarity(_combine(components, config.weights()), components)


def rank_candidates(
    seeds: Sequence[TrackFeatures],
    candidates: Iterable[TrackFeatures],
    config: ScoringConfig = DEFAULT_CONFIG,
    limit: int | None = None,
) -> list[Recommendation]:
    """Rank candidates by similarity to a user's seed songs, best first.

    `seeds` are the user's songs in rank order (best first). Each component
    is averaged across seeds, weighting seed i by seed_rank_decay ** i and
    skipping seeds where the component has no data; the averaged components
    are then combined like similarity(). Candidates that are seeds, and
    repeated candidates, are dropped. Ties are broken by track_id.
    """
    seed_ids = {seed.track_id for seed in seeds}
    weights = config.weights()
    seed_weights = [config.seed_rank_decay**i for i in range(len(seeds))]

    ranked, seen = [], set()
    for candidate in candidates:
        if candidate.track_id in seed_ids or candidate.track_id in seen:
            continue
        seen.add(candidate.track_id)

        per_seed = [similarity(candidate, seed, config).components for seed in seeds]
        components = {
            name: _weighted_mean(
                (sims[name], w) for sims, w in zip(per_seed, seed_weights)
            )
            for name in COMPONENTS
        }
        score = _combine(components, weights)
        if candidate.popularity is not None:
            score *= 1 - config.popularity_penalty * candidate.popularity / 100
        ranked.append(
            Recommendation(
                candidate.track_id, score, _reason(components, weights), components
            )
        )

    ranked.sort(key=lambda r: (-r.score, r.track_id))
    return ranked if limit is None else ranked[:limit]


def track_features_from_song(song: "Song") -> TrackFeatures:
    """Build TrackFeatures from a Song and its loaded artist credits.

    Artists are identified by their MusicVault artist ID; a song's genres are
    the union of its artists' genres, lowercased. Non-numeric audio feature
    values are ignored.
    """
    artists = [credit.artist for credit in song.artist_credits]
    return TrackFeatures(
        track_id=str(song.id),
        artists=frozenset(str(artist.id) for artist in artists),
        genres=frozenset(
            genre.strip().lower()
            for artist in artists
            for genre in artist.genres or []
            if isinstance(genre, str) and genre.strip()
        ),
        audio={
            name: float(value)
            for name, value in (song.audio_features or {}).items()
            if _is_number(value)
        },
        popularity=song.popularity,
    )


def _combine(
    components: Mapping[str, float | None], weights: Mapping[str, float]
) -> float:
    score = _weighted_mean((components[name], weights[name]) for name in COMPONENTS)
    return 0.0 if score is None else score


def _weighted_mean(pairs: Iterable[tuple[float | None, float]]) -> float | None:
    """Mean of the non-None values by weight; None if there are none."""
    total = weight_sum = 0.0
    for value, weight in pairs:
        if value is not None and weight > 0:
            total += value * weight
            weight_sum += weight
    return total / weight_sum if weight_sum else None


def _reason(
    components: Mapping[str, float | None], weights: Mapping[str, float]
) -> str | None:
    """The component with the largest weighted value; earlier ones win ties."""
    best, best_value = None, 0.0
    for name in COMPONENTS:
        value = components[name]
        if value is not None and value * weights[name] > best_value:
            best, best_value = name, value * weights[name]
    return best


def _is_number(value) -> bool:
    """A finite int or float; bools, NaN and infinities don't count."""
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
    )
