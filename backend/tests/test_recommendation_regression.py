"""Regression tests: the recommendation pipeline on a fixed dataset.

tests/data/recommendation_dataset.json holds made-up artists, songs and
listener profiles. Each profile's top songs are ranked against every song
in the dataset, going through the same steps as real data: Song and Artist
rows -> track_features_from_song -> rank_candidates.

test_rankings_match_snapshot compares every profile's full ranking (order,
scores, reasons) with tests/data/recommendation_expected.json, so any change
in recommendation behaviour fails CI. If a change is intended, regenerate
the snapshot and review its diff in the PR:

    UPDATE_RECOMMENDATION_SNAPSHOT=1 python -m pytest tests/test_recommendation_regression.py

The other tests check behaviour that should hold whatever the exact numbers
are, so a regenerated snapshot can't hide a real regression.
"""

from __future__ import annotations

import json
import os
import random

import pytest

from app.services.similarity import (
    ALGORITHM_VERSION,
    COMPONENTS,
    Recommendation,
    ScoringConfig,
    rank_candidates,
    track_features_from_song,
)
from recommendation_fixtures import (
    KEY_BY_TRACK_ID,
    PROFILES,
    SNAPSHOT_FILE,
    build_songs,
    snapshot,
)

pytestmark = pytest.mark.recommendation

SONGS = build_songs()
FEATURES = {key: track_features_from_song(song) for key, song in SONGS.items()}


def recommend(profile, config=ScoringConfig(), candidates=None):
    """Rank every dataset song (or `candidates`) for a profile."""
    seeds = [FEATURES[key] for key in PROFILES[profile]]
    pool = [FEATURES[key] for key in (candidates or FEATURES)]
    return rank_candidates(seeds, pool, config)


def keys(recommendations):
    return [KEY_BY_TRACK_ID[r.track_id] for r in recommendations]


def current_snapshot():
    return {
        "algorithm_version": ALGORITHM_VERSION,
        "profiles": {profile: snapshot(recommend(profile)) for profile in PROFILES},
    }


# --- snapshot ---------------------------------------------------------------


def test_rankings_match_snapshot():
    current = current_snapshot()
    if os.environ.get("UPDATE_RECOMMENDATION_SNAPSHOT"):
        SNAPSHOT_FILE.write_text(json.dumps(current, indent=2) + "\n")

    expected = json.loads(SNAPSHOT_FILE.read_text())
    assert (
        current["algorithm_version"] == expected["algorithm_version"]
    ), "ALGORITHM_VERSION changed; regenerate the snapshot (see module docstring)"
    for profile in PROFILES:
        assert current["profiles"][profile] == expected["profiles"][profile], (
            f"recommendations for {profile} changed. If intended, regenerate the "
            "snapshot (see module docstring) and review the diff."
        )
    assert set(expected["profiles"]) == set(PROFILES)


# --- repeatability ----------------------------------------------------------


@pytest.mark.parametrize("profile", sorted(PROFILES))
def test_results_are_repeatable(profile):
    assert recommend(profile) == recommend(profile)


@pytest.mark.parametrize("seed", range(5))
def test_candidate_order_does_not_change_results(seed):
    shuffled = list(FEATURES)
    random.Random(seed).shuffle(shuffled)
    for profile in PROFILES:
        assert recommend(profile, candidates=shuffled) == recommend(profile)


# --- result structure -------------------------------------------------------


@pytest.mark.parametrize("profile", sorted(PROFILES))
def test_results_have_the_expected_structure(profile):
    results = recommend(profile)
    seeds = set(PROFILES[profile])

    # Every dataset song except the seeds is ranked exactly once.
    assert sorted(keys(results)) == sorted(set(FEATURES) - seeds)
    for result in results:
        assert isinstance(result, Recommendation)
        assert isinstance(result.track_id, str)
        assert isinstance(result.score, float)
        assert 0.0 <= result.score <= 1.0
        assert result.reason in (*COMPONENTS, None)
        assert set(result.components) == set(COMPONENTS)
        for value in result.components.values():
            assert value is None or 0.0 <= value <= 1.0

    # Sorted best first, ties by track_id.
    order = [(-r.score, r.track_id) for r in results]
    assert order == sorted(order)


# --- multi-factor ranking ---------------------------------------------------


def test_indie_listener_gets_indie_songs_first():
    top = keys(recommend("indie_listener"))[:3]
    assert set(top) <= {"indie-4", "indie-5", "indie-6"}


def test_hiphop_listener_gets_hiphop_songs_first():
    top = keys(recommend("hiphop_listener"))[:2]
    assert set(top) <= {"hiphop-4", "hiphop-5"}


def test_shared_artists_rank_above_shared_genre_only():
    # indie-4 credits both seed artists; indie-5 only shares "indie pop".
    ranked = keys(recommend("indie_listener"))
    assert ranked.index("indie-4") < ranked.index("indie-5")


def result_for(profile, song):
    [result] = [r for r in recommend(profile) if KEY_BY_TRACK_ID[r.track_id] == song]
    return result


def test_genre_finds_new_artists_in_familiar_styles():
    # The comma-named artist shares no artist with the seeds, only genre,
    # and still ranks second.
    result = result_for("indie_listener", "indie-5")
    assert result.components["artist"] == 0.0
    assert result.components["genre"] > 0.0
    assert keys(recommend("indie_listener"))[1] == "indie-5"


def test_unrelated_styles_rank_last():
    ranked = keys(recommend("indie_listener"))
    for unrelated in ("hiphop-1", "hiphop-3", "electronic-1"):
        assert ranked.index(unrelated) > ranked.index("indie-5")


def test_mixed_listener_gets_matches_from_each_style():
    top = set(keys(recommend("mixed_listener"))[:6])
    assert top & {"indie-1", "indie-2"}
    assert top & {"electronic-2", "electronic-3"}
    assert top & {"hiphop-2", "jazz-1"}


def test_audio_breaks_ties_between_same_genre_songs():
    # Same artist and genres as the seed; audio decides.
    results = {
        KEY_BY_TRACK_ID[r.track_id]: r
        for r in recommend("hiphop_listener", candidates=["hiphop-4", "hiphop-5"])
    }
    assert results["hiphop-4"].components["audio"] is not None
    assert results["hiphop-4"].score > results["hiphop-5"].score


def test_turning_off_genre_and_audio_ranks_by_artist_only():
    config = ScoringConfig(artist_weight=1, genre_weight=0, audio_weight=0)
    results = recommend("indie_listener", config)
    assert keys(results)[0] == "indie-4"
    for result in results:
        assert result.score == pytest.approx(result.components["artist"] or 0.0)


def test_popularity_penalty_moves_lesser_known_songs_up():
    default = keys(recommend("hiphop_listener"))
    penalised = keys(recommend("hiphop_listener", ScoringConfig(popularity_penalty=1)))
    # hiphop-5 (popularity 22) passes hiphop-4 (popularity 76).
    assert default.index("hiphop-4") < default.index("hiphop-5")
    assert penalised.index("hiphop-5") < penalised.index("hiphop-4")


# --- empty and missing data -------------------------------------------------


def test_empty_profile_returns_every_song_with_zero_score():
    results = recommend("empty_listener")
    assert len(results) == len(FEATURES)
    assert {(r.score, r.reason) for r in results} == {(0.0, None)}


def test_empty_candidate_list_returns_nothing():
    seeds = [FEATURES[key] for key in PROFILES["indie_listener"]]
    assert rank_candidates(seeds, []) == []


def test_seeds_without_audio_still_find_the_same_artists():
    # indie-3 shares indie-6's artist and genres; unknown-2 shares only
    # unknown-1's artist, which has no genres.
    results = recommend("sparse_listener")
    assert keys(results)[:2] == ["indie-3", "unknown-2"]
    assert all(r.components["audio"] is None for r in results)
    assert results[1].reason == "artist"


def test_candidates_missing_seed_data_rank_below_real_matches():
    # These songs have one usable audio feature at most; in similarity-v1
    # they outranked real indie matches on that alone.
    ranked = keys(recommend("indie_listener"))
    for sparse in ("messy-1", "unfiled-1", "unknown-2", "no-artists-1"):
        assert ranked.index(sparse) > ranked.index("indie-6")
        assert result_for("indie_listener", sparse).score == 0.0


def test_unusable_metadata_is_ignored_not_fatal():
    assert FEATURES["messy-1"].genres == frozenset()
    assert FEATURES["messy-1"].audio == {"valence": 0.5}
    assert FEATURES["unfiled-1"].audio == {"energy": 0.6}
    assert FEATURES["indie-5"].genres == frozenset({"indie pop"})
    assert FEATURES["no-artists-1"].artists == frozenset()

    results = recommend("messy_listener")
    assert len(results) == len(FEATURES) - len(PROFILES["messy_listener"])


def test_songs_without_metadata_score_zero_not_error():
    for profile in PROFILES:
        if "no-artists-1" in PROFILES[profile]:
            continue
        result = result_for(profile, "no-artists-1")
        assert result.score == 0.0
        assert result.reason is None
