"""Swipe-deck ranking: turn the artists a graph walk reaches into an ordered
deck of track cards.

The walk (graph_walk) says which artists are near the user's taste, the
similarity scorer (similarity) says which of their tracks match the user's
songs, and a discovery multiplier pushes well-known artists down. Variety
rules then thin out decks that repeat an artist or a tag.

Everything here is a pure function of its inputs: no database access, no
clock, no randomness. The same catalog, seeds and config always give the same
deck in the same order. See docs/graph-engine.md for the formulas, the
default weights and why they were chosen.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass

from app.services.graph_walk import (
    ALGORITHM_VERSION,
    DEFAULT_GRAPH_CONFIG,
    Graph,
    GraphConfig,
    UserSeeds,
    personalized_pagerank,
    reason_path,
    select_candidates,
    start_vector,
)
from app.services.similarity import (
    DEFAULT_CONFIG,
    ScoringConfig,
    TrackFeatures,
    rank_candidates,
)

# ALGORITHM_VERSION is re-exported: a stored deck covers both stages.
__all__ = [
    "ALGORITHM_VERSION",
    "DEFAULT_DECK_CONFIG",
    "CatalogArtist",
    "CatalogTrack",
    "DeckConfig",
    "DeckItem",
    "check_variety",
    "fans_percentiles",
    "rank_deck",
]


@dataclass(frozen=True)
class CatalogArtist:
    """What the deck knows about one artist besides the graph."""

    artist_id: str
    fans: int | None = None
    top_tag: str | None = None


@dataclass(frozen=True)
class CatalogTrack:
    artist_id: str
    features: TrackFeatures

    @property
    def track_id(self) -> str:
        return self.features.track_id


@dataclass(frozen=True)
class DeckConfig:
    """Tunable parameters. The defaults are documented baselines."""

    # Relative weights of the walk score and the similarity score.
    graph_weight: float = 0.6
    similarity_weight: float = 0.4
    # At most this much of a card's score is taken off for being well known.
    discovery_penalty: float = 0.3
    unknown_fans_pct: float = 0.5
    max_tracks_per_artist: int = 2
    max_same_tag_run: int = 3
    graph: GraphConfig = DEFAULT_GRAPH_CONFIG
    scoring: ScoringConfig = DEFAULT_CONFIG

    def __post_init__(self):
        if self.graph_weight < 0 or self.similarity_weight < 0:
            raise ValueError("deck weights must not be negative")
        if self.graph_weight + self.similarity_weight <= 0:
            raise ValueError("at least one deck weight must be positive")
        if not 0 <= self.discovery_penalty <= 1:
            raise ValueError("discovery_penalty must be in [0, 1]")
        if not 0 <= self.unknown_fans_pct <= 1:
            raise ValueError("unknown_fans_pct must be in [0, 1]")
        if self.max_tracks_per_artist < 1:
            raise ValueError("max_tracks_per_artist must be at least 1")
        if self.max_same_tag_run < 1:
            raise ValueError("max_same_tag_run must be at least 1")


DEFAULT_DECK_CONFIG = DeckConfig()


@dataclass(frozen=True)
class DeckItem:
    """One card: its score, the three parts it came from, and its path."""

    track_id: str
    artist_id: str
    score: float
    components: Mapping[str, float]
    reason_path: tuple[str, ...]


def fans_percentiles(
    artists: Iterable[CatalogArtist], unknown: float = 0.5
) -> dict[str, float]:
    """Each artist's rank by fan count, 0 for the fewest and 1 for the most.

    Ties share the midrank, a single known artist is 0, and an artist whose
    fan count is unknown gets `unknown`.
    """
    percentiles: dict[str, float] = {}
    known: list[tuple[int, str]] = []
    for artist in artists:
        if artist.fans is None:
            percentiles[artist.artist_id] = unknown
        else:
            known.append((artist.fans, artist.artist_id))

    total = len(known)
    if total == 1:
        percentiles[known[0][1]] = 0.0
        return percentiles

    known.sort()
    index = 0
    while index < total:
        end = index
        fans = known[index][0]
        while end < total and known[end][0] == fans:
            end += 1
        percentile = (index + (end - index - 1) / 2) / (total - 1)
        for _, artist_id in known[index:end]:
            percentiles[artist_id] = percentile
        index = end
    return percentiles


def rank_deck(
    graph: Graph,
    seeds: UserSeeds,
    seed_features: Sequence[TrackFeatures],
    artists: Iterable[CatalogArtist],
    tracks: Iterable[CatalogTrack],
    limit: int = 20,
    exclude: Iterable[str] = (),
    config: DeckConfig = DEFAULT_DECK_CONFIG,
) -> list[DeckItem]:
    """The user's next `limit` cards, best first, ties broken by track id.

    Candidate artists come from a personalized PageRank walk over `graph`,
    their tracks are scored against `seed_features`, and the result is cut
    down by the variety rules. With no seeds to walk from, the deck falls
    back to the least-known tracks in the catalog. Tracks in `exclude`,
    tracks the user has already rated the artist of, and the seed tracks
    themselves are never in the deck.
    """
    if limit < 0:
        raise ValueError("limit must not be negative")

    catalog = {artist.artist_id: artist for artist in artists}
    percentiles = fans_percentiles(catalog.values(), config.unknown_fans_pct)
    unknown_pct = config.unknown_fans_pct
    penalty = config.discovery_penalty

    excluded = set(exclude)
    by_artist: dict[str, list[CatalogTrack]] = {}
    seen: set[str] = set()
    for track in tracks:
        track_id = track.track_id
        if track_id in excluded or track_id in seen:
            continue
        seen.add(track_id)
        by_artist.setdefault(track.artist_id, []).append(track)

    start = start_vector(seeds, config.graph)
    judged = seeds.preferred() | seeds.removed(config.graph)

    if not start:
        cold = sorted(
            (percentiles.get(artist_id, unknown_pct), track.track_id, artist_id)
            for artist_id, group in by_artist.items()
            if artist_id not in judged
            for track in group
        )
        ranked = [
            DeckItem(
                track_id=track_id,
                artist_id=artist_id,
                score=1 - penalty * percentile,
                components={
                    "graph": 0.0,
                    "similarity": 0.0,
                    "discovery": 1 - penalty * percentile,
                },
                reason_path=(),
            )
            for percentile, track_id, artist_id in cold
        ]
        return _apply_variety(ranked, catalog, limit, config)

    walk = personalized_pagerank(graph, start, config.graph)
    candidates = select_candidates(walk, seeds, start, config.graph)
    if not candidates:
        return []
    max_walk = max(score for _, score in candidates)

    candidate_tracks = [
        track for artist_id, _ in candidates for track in by_artist.get(artist_id, ())
    ]
    similarities = {
        recommendation.track_id: recommendation.score
        for recommendation in rank_candidates(
            seed_features,
            [track.features for track in candidate_tracks],
            config.scoring,
        )
    }
    graph_scores = {artist_id: score / max_walk for artist_id, score in candidates}
    paths: dict[str, tuple[str, ...]] = {}

    ranked = []
    for track in candidate_tracks:
        similarity = similarities.get(track.track_id)
        if similarity is None:
            continue
        artist_id = track.artist_id
        graph_score = graph_scores[artist_id]
        discovery = 1 - penalty * percentiles.get(artist_id, unknown_pct)
        path = paths.get(artist_id)
        if path is None:
            paths[artist_id] = path = reason_path(walk, artist_id)
        ranked.append(
            DeckItem(
                track_id=track.track_id,
                artist_id=artist_id,
                score=(
                    config.graph_weight * graph_score
                    + config.similarity_weight * similarity
                )
                * discovery,
                components={
                    "graph": graph_score,
                    "similarity": similarity,
                    "discovery": discovery,
                },
                reason_path=path,
            )
        )

    ranked.sort(key=lambda item: (-item.score, item.track_id))
    return _apply_variety(ranked, catalog, limit, config)


def check_variety(
    items: Sequence[DeckItem],
    artists: Mapping[str, CatalogArtist],
    config: DeckConfig = DEFAULT_DECK_CONFIG,
) -> list[str]:
    """Re-check a finished deck against the variety rules.

    One message per violation, or an empty list when the deck is clean.
    """
    problems = []
    counts = Counter(item.artist_id for item in items)
    for artist_id, count in sorted(counts.items()):
        if count > config.max_tracks_per_artist:
            problems.append(f"artist {artist_id} has {count} tracks")

    runs: list[tuple[str, int, int]] = []
    for position, item in enumerate(items):
        tag = _top_tag(artists, item.artist_id)
        if tag is None:
            continue
        if runs and runs[-1][0] == tag and runs[-1][2] == position - 1:
            runs[-1] = (tag, runs[-1][1], position)
        else:
            runs.append((tag, position, position))
    for tag, first, last in runs:
        if last - first + 1 > config.max_same_tag_run:
            problems.append(f"cards {first + 1}-{last + 1} share tag '{tag}'")
    return problems


def _apply_variety(
    ranked: Sequence[DeckItem],
    artists: Mapping[str, CatalogArtist],
    limit: int,
    config: DeckConfig,
) -> list[DeckItem]:
    """Fill each slot with the best remaining item that breaks no rule.

    An item skipped only for the tag run stays available for later slots.
    """
    kept: list[DeckItem] = []
    remaining = list(ranked)
    per_artist: Counter[str] = Counter()
    run_tag: str | None = None
    run_length = 0
    while len(kept) < limit:
        chosen = None
        for index, item in enumerate(remaining):
            if per_artist[item.artist_id] >= config.max_tracks_per_artist:
                continue
            tag = _top_tag(artists, item.artist_id)
            if tag is None or tag != run_tag or run_length < config.max_same_tag_run:
                chosen = index
                break
        if chosen is None:
            break
        item = remaining.pop(chosen)
        tag = _top_tag(artists, item.artist_id)
        kept.append(item)
        per_artist[item.artist_id] += 1
        if tag is not None and tag == run_tag:
            run_length += 1
        else:
            run_tag, run_length = tag, 1
    return kept


def _top_tag(artists: Mapping[str, CatalogArtist], artist_id: str) -> str | None:
    artist = artists.get(artist_id)
    return artist.top_tag if artist is not None else None
