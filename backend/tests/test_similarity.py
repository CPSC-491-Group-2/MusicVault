"""Unit tests for similarity scoring and candidate ranking.

All pure functions: no database, no network.
"""

from __future__ import annotations

import math
import uuid

import pytest

from app.services.similarity import (
    ALGORITHM_VERSION,
    ScoringConfig,
    TrackFeatures,
    artist_similarity,
    audio_similarity,
    genre_similarity,
    overlap,
    rank_candidates,
    similarity,
    track_features_from_song,
)
from models.artist import Artist, SongArtist
from models.song import Song

pytestmark = pytest.mark.recommendation


def track(track_id, artists=(), genres=(), audio=None, popularity=None):
    return TrackFeatures(
        track_id=track_id,
        artists=frozenset(artists),
        genres=frozenset(genres),
        audio=audio or {},
        popularity=popularity,
    )


def test_algorithm_version_is_set():
    assert ALGORITHM_VERSION == "similarity-v2"


# --- overlap / artist / genre -----------------------------------------------


@pytest.mark.parametrize(
    "a, b, expected",
    [
        ({"x"}, {"x"}, 1.0),
        ({"x"}, {"y"}, 0.0),
        ({"x", "y"}, {"y", "z"}, 1 / 3),
        ({"x", "y"}, {"x", "y", "z", "w"}, 0.5),
    ],
)
def test_overlap_is_shared_over_all(a, b, expected):
    assert overlap(frozenset(a), frozenset(b)) == pytest.approx(expected)


@pytest.mark.parametrize("a, b", [(set(), {"x"}), ({"x"}, set()), (set(), set())])
def test_overlap_is_unknown_when_either_side_is_empty(a, b):
    assert overlap(frozenset(a), frozenset(b)) is None


def test_artist_similarity_uses_artists_only():
    a = track("a", artists={"artist-1", "artist-2"}, genres={"pop"})
    b = track("b", artists={"artist-2"}, genres={"rock"})
    assert artist_similarity(a, b) == pytest.approx(0.5)


def test_genre_similarity_uses_genres_only():
    a = track("a", artists={"artist-1"}, genres={"pop", "dance pop"})
    b = track("b", artists={"artist-2"}, genres={"pop"})
    assert genre_similarity(a, b) == pytest.approx(0.5)


def test_component_scores_are_symmetric():
    a = track("a", {"x", "y"}, {"pop"}, {"energy": 0.2, "tempo": 100})
    b = track("b", {"y"}, {"pop", "rock"}, {"energy": 0.9, "tempo": 130})
    assert similarity(a, b) == similarity(b, a)


# --- audio ------------------------------------------------------------------


def test_identical_audio_features_score_one():
    audio = {"energy": 0.7, "danceability": 0.5, "tempo": 120}
    assert audio_similarity(track("a", audio=audio), track("b", audio=audio)) == 1.0


def test_unit_scale_features_use_a_half_scale_range():
    a = track("a", audio={"energy": 0.2, "valence": 0.5})
    b = track("b", audio={"energy": 0.6, "valence": 0.5})
    # Distances 0.4 / 0.5 = 0.8 and 0.0 -> mean distance 0.4.
    assert audio_similarity(a, b) == pytest.approx(0.6)


def test_unit_scale_differences_of_half_or_more_count_as_completely_different():
    a, b = track("a", audio={"energy": 0.2}), track("b", audio={"energy": 0.9})
    assert audio_similarity(a, b) == 0.0


def test_audio_needs_the_minimum_number_of_shared_features():
    a = track("a", audio={"energy": 0.5, "valence": 0.5, "tempo": 100})
    b = track("b", audio={"energy": 0.5, "valence": 0.5})
    assert audio_similarity(a, b, min_features=3) is None
    assert audio_similarity(a, b, min_features=2) == 1.0


def test_tempo_is_scaled_by_its_range_and_capped():
    a = track("a", audio={"tempo": 100})
    assert audio_similarity(a, track("b", audio={"tempo": 130})) == pytest.approx(0.5)
    assert audio_similarity(a, track("c", audio={"tempo": 220})) == 0.0


def test_tempo_range_is_tunable():
    a, b = track("a", audio={"tempo": 100}), track("b", audio={"tempo": 130})
    assert audio_similarity(a, b, {"tempo": 120.0}) == pytest.approx(0.75)


def test_only_features_both_songs_have_are_compared():
    a = track("a", audio={"energy": 0.5, "tempo": 90})
    b = track("b", audio={"energy": 0.5, "danceability": 0.1})
    assert audio_similarity(a, b) == 1.0


def test_unknown_feature_names_are_ignored():
    a = track("a", audio={"energy": 0.5, "loudness": -5})
    b = track("b", audio={"energy": 0.5, "loudness": -30})
    assert audio_similarity(a, b) == 1.0


@pytest.mark.parametrize(
    "bad_value", [None, "0.5", True, math.nan, math.inf, -math.inf]
)
def test_unusable_audio_values_are_skipped(bad_value):
    a = track("a", audio={"energy": bad_value, "valence": 0.3})
    b = track("b", audio={"energy": 0.5, "valence": 0.3})
    assert audio_similarity(a, b) == 1.0


def test_audio_is_unknown_without_shared_features():
    assert audio_similarity(track("a"), track("b", audio={"energy": 1})) is None
    a, b = track("a", audio={"energy": 1}), track("b", audio={"tempo": 1})
    assert audio_similarity(a, b) is None


# --- combined score ---------------------------------------------------------


# Three shared features, each 0.25 apart (half their 0.5 range): audio 0.5.
AUDIO_A = {"energy": 0.5, "valence": 0.5, "danceability": 0.5}
AUDIO_B = {"energy": 0.25, "valence": 0.25, "danceability": 0.25}


def test_score_is_weighted_mean_of_components():
    a = track("a", {"x"}, {"pop"}, AUDIO_A)
    b = track("b", {"x"}, {"rock"}, AUDIO_B)
    result = similarity(a, b)

    assert result.components == {"artist": 1.0, "genre": 0.0, "audio": 0.5}
    # (0.35 * 1 + 0.35 * 0 + 0.30 * 0.5) / 1.0
    assert result.score == pytest.approx(0.5)


def test_missing_components_are_left_out_and_weights_rescaled():
    a = track("a", artists={"x"}, audio=AUDIO_A)
    b = track("b", artists={"x"}, audio=AUDIO_B)
    result = similarity(a, b)

    assert result.components["genre"] is None
    # (0.35 * 1 + 0.30 * 0.5) / (0.35 + 0.30)
    assert result.score == pytest.approx(0.5 / 0.65)


def test_too_few_shared_audio_features_leave_audio_out():
    a = track("a", artists={"x"}, audio={"energy": 0.5})
    b = track("b", artists={"x"}, audio={"energy": 0.0})
    result = similarity(a, b)
    assert result.components["audio"] is None
    assert result.score == 1.0


def test_min_audio_features_is_tunable():
    a = track("a", audio={"energy": 0.5})
    b = track("b", audio={"energy": 0.25})
    result = similarity(a, b, ScoringConfig(min_audio_features=1))
    assert result.components["audio"] == pytest.approx(0.5)


def test_artist_only_data_scores_on_artists_alone():
    result = similarity(track("a", artists={"x"}), track("b", artists={"x"}))
    assert result.score == 1.0


def test_no_shared_data_scores_zero():
    result = similarity(track("a", artists={"x"}), track("b", genres={"pop"}))
    assert result.components == {"artist": None, "genre": None, "audio": None}
    assert result.score == 0.0


def test_zero_weight_turns_a_component_off():
    config = ScoringConfig(artist_weight=0, genre_weight=1, audio_weight=0)
    a = track("a", {"x"}, {"pop"}, {"energy": 0.0})
    b = track("b", {"x"}, {"rock"}, {"energy": 0.0})
    assert similarity(a, b, config).score == 0.0


def test_weights_are_relative():
    a = track("a", {"x"}, {"pop"}, {"energy": 0.1})
    b = track("b", {"x", "y"}, {"pop", "rock"}, {"energy": 0.6})
    doubled = ScoringConfig(artist_weight=0.7, genre_weight=0.7, audio_weight=0.6)
    assert similarity(a, b, doubled).score == pytest.approx(similarity(a, b).score)


def test_scores_stay_between_zero_and_one():
    a = track("a", {"x", "y"}, {"pop"}, {"energy": 0.0, "tempo": 60})
    b = track("b", {"y", "z"}, {"pop", "edm"}, {"energy": 1.0, "tempo": 200})
    assert 0.0 <= similarity(a, b).score <= 1.0


# --- config validation ------------------------------------------------------


@pytest.mark.parametrize(
    "kwargs",
    [
        {"artist_weight": -0.1},
        {"artist_weight": 0, "genre_weight": 0, "audio_weight": 0},
        {"seed_rank_decay": 0},
        {"seed_rank_decay": 1.5},
        {"popularity_penalty": -0.1},
        {"popularity_penalty": 1.1},
        {"audio_feature_ranges": {"tempo": 0}},
        {"min_audio_features": 0},
        {"missing_data_score": -0.1},
        {"missing_data_score": 1.5},
    ],
)
def test_invalid_config_is_rejected(kwargs):
    with pytest.raises(ValueError):
        ScoringConfig(**kwargs)


def test_default_weights_are_documented_values():
    assert ScoringConfig().weights() == {"artist": 0.35, "genre": 0.35, "audio": 0.30}


# --- ranking ----------------------------------------------------------------


def test_candidates_are_ranked_best_first():
    seeds = [track("seed", artists={"x"}, genres={"pop"})]
    candidates = [
        track("far", artists={"z"}, genres={"metal"}),
        track("close", artists={"x"}, genres={"pop"}),
        track("middle", artists={"z"}, genres={"pop"}),
    ]
    ranked = rank_candidates(seeds, candidates)
    assert [r.track_id for r in ranked] == ["close", "middle", "far"]


def test_ties_are_broken_by_track_id():
    seeds = [track("seed", artists={"x"})]
    candidates = [track(name, artists={"x"}) for name in ("c", "a", "b")]
    assert [r.track_id for r in rank_candidates(seeds, candidates)] == ["a", "b", "c"]


def test_ranking_is_deterministic_regardless_of_candidate_order():
    seeds = [
        track("s1", {"x"}, {"pop"}, {"energy": 0.8}),
        track("s2", {"y"}, {"rock"}, {"energy": 0.3}),
    ]
    candidates = [
        track(f"c{i}", {"x", "y"} if i % 2 else {"z"}, {"pop"}, {"energy": i / 10})
        for i in range(10)
    ]
    forward = rank_candidates(seeds, candidates)
    backward = rank_candidates(seeds, list(reversed(candidates)))
    assert forward == backward
    assert forward == rank_candidates(seeds, candidates)


def test_seeds_and_repeated_candidates_are_dropped():
    seeds = [track("seed", artists={"x"})]
    candidates = [
        track("seed", artists={"x"}),
        track("other", artists={"x"}),
        track("other", artists={"x"}),
    ]
    assert [r.track_id for r in rank_candidates(seeds, candidates)] == ["other"]


def test_higher_ranked_seeds_count_more():
    seeds = [track("top", artists={"a"}), track("second", artists={"b"})]
    candidates = [track("like-top", artists={"a"}), track("like-second", artists={"b"})]
    ranked = rank_candidates(seeds, candidates)

    assert [r.track_id for r in ranked] == ["like-top", "like-second"]
    # Seed weights 1 and 0.9: like-top scores 1 / 1.9.
    assert ranked[0].score == pytest.approx(1 / 1.9)
    assert ranked[1].score == pytest.approx(0.9 / 1.9)


def test_no_decay_counts_seeds_equally():
    seeds = [track("top", artists={"a"}), track("second", artists={"b"})]
    candidates = [track("like-top", artists={"a"}), track("like-second", artists={"b"})]
    ranked = rank_candidates(seeds, candidates, ScoringConfig(seed_rank_decay=1))
    assert ranked[0].score == ranked[1].score == pytest.approx(0.5)


def test_seeds_without_a_component_do_not_dilute_it():
    seeds = [
        track("with-genre", artists={"a"}, genres={"pop"}),
        track("no-genre", artists={"a"}),
    ]
    [result] = rank_candidates(seeds, [track("c", artists={"a"}, genres={"pop"})])
    assert result.components["genre"] == 1.0
    assert result.score == 1.0


def test_candidate_missing_data_the_seed_has_scores_zero():
    seeds = [track("seed", artists={"x"}, genres={"pop"})]
    [result] = rank_candidates(seeds, [track("c", artists={"x"})])
    # Genre counts as no match instead of being left out: (0.35 * 1) / 0.70.
    assert result.components["genre"] == 0.0
    assert result.score == pytest.approx(0.5)


def test_sparse_candidates_rank_below_real_matches():
    seeds = [track("seed", {"x"}, {"pop"}, AUDIO_A)]
    candidates = [
        # Only one audio feature, which happens to match.
        track("sparse", artists={"z"}, audio={"energy": 0.5}),
        track("real-match", artists={"z"}, genres={"pop"}, audio=AUDIO_B),
    ]
    ranked = rank_candidates(seeds, candidates)
    assert [r.track_id for r in ranked] == ["real-match", "sparse"]
    assert ranked[1].score == 0.0


def test_missing_data_score_is_tunable():
    seeds = [track("seed", artists={"x"}, genres={"pop"})]
    config = ScoringConfig(missing_data_score=0.5)
    [result] = rank_candidates(seeds, [track("c", artists={"x"})], config)
    assert result.components["genre"] == 0.5
    assert result.score == pytest.approx(0.75)


def test_data_neither_song_has_is_still_left_out():
    seeds = [track("seed", artists={"x"})]
    [result] = rank_candidates(seeds, [track("c", artists={"x"})])
    assert result.components == {"artist": 1.0, "genre": None, "audio": None}
    assert result.score == 1.0


def test_limit_keeps_the_top_results():
    seeds = [track("seed", artists={"x"})]
    candidates = [track(name, artists={"x"}) for name in ("a", "b", "c")]
    assert [r.track_id for r in rank_candidates(seeds, candidates, limit=2)] == [
        "a",
        "b",
    ]


def test_no_seeds_scores_every_candidate_zero():
    ranked = rank_candidates([], [track("b", artists={"x"}), track("a")])
    assert [(r.track_id, r.score, r.reason) for r in ranked] == [
        ("a", 0.0, None),
        ("b", 0.0, None),
    ]


def test_popularity_penalty_favours_lesser_known_songs():
    seeds = [track("seed", artists={"x"})]
    candidates = [
        track("hit", artists={"x"}, popularity=90),
        track("deep-cut", artists={"x"}, popularity=10),
        track("unknown", artists={"x"}),
    ]
    config = ScoringConfig(popularity_penalty=0.5)
    ranked = {r.track_id: r.score for r in rank_candidates(seeds, candidates, config)}

    assert ranked["hit"] == pytest.approx(1 - 0.5 * 0.9)
    assert ranked["deep-cut"] == pytest.approx(1 - 0.5 * 0.1)
    assert ranked["unknown"] == 1.0


def test_popularity_is_ignored_by_default():
    seeds = [track("seed", artists={"x"})]
    [result] = rank_candidates(seeds, [track("hit", artists={"x"}, popularity=100)])
    assert result.score == 1.0


@pytest.mark.parametrize(
    "candidate, expected_reason",
    [
        (track("c", artists={"x"}, genres={"jazz"}), "artist"),
        (track("c", artists={"z"}, genres={"pop"}), "genre"),
        (track("c", artists={"z"}, audio=AUDIO_A), "audio"),
        (track("c", artists={"z"}), None),
    ],
)
def test_reason_is_the_strongest_component(candidate, expected_reason):
    seeds = [track("seed", {"x"}, {"pop"}, AUDIO_A)]
    [result] = rank_candidates(seeds, [candidate])
    assert result.reason == expected_reason


def test_reason_ties_go_to_the_earlier_component():
    seeds = [track("seed", artists={"x"}, genres={"pop"})]
    [result] = rank_candidates(seeds, [track("c", artists={"x"}, genres={"pop"})])
    assert result.reason == "artist"


# --- building features from a Song -------------------------------------------


def make_artist(name, genres=None):
    return Artist(id=uuid.uuid4(), name=name, genres=genres)


def make_song(artists, audio_features=None, popularity=None):
    song = Song(
        id=uuid.uuid4(),
        title="Song",
        artist_name=", ".join(a.name for a in artists),
        audio_features=audio_features,
        popularity=popularity,
    )
    song.artist_credits = [
        SongArtist(artist=artist, position=position)
        for position, artist in enumerate(artists, start=1)
    ]
    return song


def test_features_from_song_use_artist_ids_not_names():
    first, second = make_artist("Tyler, The Creator"), make_artist("Kali Uchis")
    features = track_features_from_song(make_song([first, second], popularity=55))

    assert features.artists == frozenset({str(first.id), str(second.id)})
    assert features.popularity == 55


def test_song_genres_are_the_union_of_its_artists_genres():
    song = make_song(
        [
            make_artist("A", ["Pop", "dance pop"]),
            make_artist("B", ["pop ", "", 7]),
            make_artist("C", None),
        ]
    )
    assert track_features_from_song(song).genres == frozenset({"pop", "dance pop"})


def test_song_audio_features_keep_only_numbers():
    song = make_song(
        [make_artist("A")],
        audio_features={"energy": 0.8, "tempo": 120, "key": "C", "live": True},
    )
    assert track_features_from_song(song).audio == {"energy": 0.8, "tempo": 120.0}


def test_song_without_data_has_empty_features():
    features = track_features_from_song(make_song([]))
    assert features.artists == features.genres == frozenset()
    assert features.audio == {}
    assert features.popularity is None
