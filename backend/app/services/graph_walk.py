"""Artist graph walk: build an artist-to-artist graph from related-artist
edges, push a personalized PageRank from a user's seeds, and read candidates
with the path that explains each one.

Everything here is a pure function of its inputs: no database access, no
clock, no randomness. The same edges, seeds and config always give the same
scores in the same order. See docs/graph-engine.md for the formulas, the
default weights and why they were chosen.
"""

from __future__ import annotations

import math
from collections import deque
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from types import MappingProxyType

ALGORITHM_VERSION = "graph-v1"

PROVIDERS = ("lastfm_similar", "deezer_related", "mb_relation", "co_credit")

# How far each source of "these two artists are related" is trusted.
DEFAULT_PROVIDER_WEIGHTS = MappingProxyType(
    {
        "lastfm_similar": 1.0,
        "deezer_related": 0.8,
        "mb_relation": 0.6,
        "co_credit": 0.5,
    }
)


@dataclass(frozen=True)
class Edge:
    """One provider's claim that `target` is related to `source`."""

    source: str
    target: str
    provider: str
    score: float


@dataclass(frozen=True)
class GraphConfig:
    """Tunable parameters. The defaults are documented baselines."""

    provider_weights: Mapping[str, float] = DEFAULT_PROVIDER_WEIGHTS
    # Divide an artist's incoming weight by log(2 + in-degree), so artists
    # everything points at don't swamp the walk.
    hub_damping: bool = True
    # The artist of top track r (0 = the user's top track) starts with
    # top_track_decay ** r of the mass a saved artist gets.
    top_track_decay: float = 0.9
    # Dislikes at or above this count drop the artist from the walk entirely.
    dislike_threshold: int = 2
    # Share of the mass at a node that settles there instead of walking on.
    restart_probability: float = 0.15
    # Mass below this is never pushed further: the accuracy/time dial.
    epsilon: float = 1e-4
    max_hops: int = 3
    candidate_limit: int = 200

    def __post_init__(self):
        if any(weight < 0 for weight in self.provider_weights.values()):
            raise ValueError("provider weights must not be negative")
        unknown = sorted(set(self.provider_weights) - set(PROVIDERS))
        if unknown:
            raise ValueError(f"unknown providers: {', '.join(unknown)}")
        if not 0 < self.top_track_decay <= 1:
            raise ValueError("top_track_decay must be in (0, 1]")
        if self.dislike_threshold < 1:
            raise ValueError("dislike_threshold must be at least 1")
        if not 0 < self.restart_probability < 1:
            raise ValueError("restart_probability must be in (0, 1)")
        if self.epsilon <= 0:
            raise ValueError("epsilon must be positive")
        if self.max_hops < 1:
            raise ValueError("max_hops must be at least 1")
        if self.candidate_limit < 1:
            raise ValueError("candidate_limit must be at least 1")


DEFAULT_GRAPH_CONFIG = GraphConfig()


@dataclass(frozen=True)
class UserSeeds:
    """Where a user's walk starts, and which artists it must avoid."""

    saved_artists: frozenset[str] = frozenset()
    # The artist of each top track, rank 0 first; repeats allowed.
    top_track_artists: tuple[str, ...] = ()
    liked_artists: frozenset[str] = frozenset()
    dislikes: Mapping[str, int] = field(default_factory=dict)

    def preferred(self) -> frozenset[str]:
        """Artists the user has already judged, so not worth recommending."""
        return frozenset(self.liked_artists) | {
            artist for artist, count in self.dislikes.items() if count > 0
        }

    def removed(self, config: GraphConfig = DEFAULT_GRAPH_CONFIG) -> frozenset[str]:
        return frozenset(
            artist
            for artist, count in self.dislikes.items()
            if count >= config.dislike_threshold
        )


@dataclass(frozen=True)
class Graph:
    out: Mapping[str, tuple[tuple[str, float], ...]]
    weights: Mapping[str, Mapping[str, float]]
    # Distinct sources pointing at an artist, as used by hub damping.
    in_degree: Mapping[str, int]


@dataclass(frozen=True)
class WalkResult:
    scores: Mapping[str, float]
    hops: Mapping[str, int]
    predecessor: Mapping[str, str]


def build_graph(
    edges: Iterable[Edge], config: GraphConfig = DEFAULT_GRAPH_CONFIG
) -> Graph:
    """Combine provider edges into one weighted graph, row-normalized.

    Self-loops and unknown providers are ignored, and a repeated
    (source, target, provider) keeps its highest score. The weight of a pair
    is the provider-weighted sum of its scores, divided by
    log(2 + in-degree of the target) when hub damping is on.
    """
    provider_weights = config.provider_weights
    scored: dict[tuple[str, str, str], float] = {}
    for edge in edges:
        if edge.source == edge.target or edge.provider not in provider_weights:
            continue
        key = (edge.source, edge.target, edge.provider)
        previous = scored.get(key)
        if previous is None or edge.score > previous:
            scored[key] = edge.score

    in_sources: dict[str, set[str]] = {}
    combined: dict[str, dict[str, float]] = {}
    for (source, target, provider), score in scored.items():
        in_sources.setdefault(target, set()).add(source)
        row = combined.get(source)
        if row is None:
            combined[source] = row = {}
        row[target] = row.get(target, 0.0) + provider_weights[provider] * score

    in_degree = {target: len(sources) for target, sources in sorted(in_sources.items())}

    out: dict[str, tuple[tuple[str, float], ...]] = {}
    weights: dict[str, dict[str, float]] = {}
    for source in sorted(combined):
        row = {}
        for target in sorted(combined[source]):
            weight = combined[source][target]
            if config.hub_damping:
                weight /= math.log(2 + in_degree.get(target, 0))
            if weight > 0:
                row[target] = weight
        if not row:
            continue
        total = sum(row.values())
        weights[source] = row
        out[source] = tuple((target, w / total) for target, w in row.items())

    return Graph(out=out, weights=weights, in_degree=in_degree)


def start_vector(
    seeds: UserSeeds, config: GraphConfig = DEFAULT_GRAPH_CONFIG
) -> dict[str, float]:
    """The walk's starting mass per artist, summing to 1.

    A saved artist contributes 1, the artist of top track r contributes
    top_track_decay ** r, and an artist counted twice gets both. Artists the
    user has disliked enough are dropped. Empty when nothing is left.
    """
    mass: dict[str, float] = {}
    for artist in sorted(seeds.saved_artists):
        mass[artist] = mass.get(artist, 0.0) + 1.0
    for rank, artist in enumerate(seeds.top_track_artists):
        mass[artist] = mass.get(artist, 0.0) + config.top_track_decay**rank
    for artist in seeds.removed(config):
        mass.pop(artist, None)

    total = sum(mass.values())
    if total <= 0:
        return {}
    return {artist: value / total for artist, value in sorted(mass.items())}


def personalized_pagerank(
    graph: Graph,
    start: Mapping[str, float],
    config: GraphConfig = DEFAULT_GRAPH_CONFIG,
) -> WalkResult:
    """Local-push personalized PageRank (Andersen-Chung-Lang).

    Mass is pushed outward from the start artists until every artist holds
    less than epsilon, so only the neighbourhood that matters is visited.
    Mass reaching an artist max_hops from the start, or one with no outgoing
    edges, stops there. Each reached artist also gets the hop distance and
    the neighbour one hop closer to the start that sent it the most mass,
    which is what reason_path() walks back.
    """
    out = graph.out
    alpha = config.restart_probability
    epsilon = config.epsilon
    max_hops = config.max_hops
    spread_share = 1.0 - alpha

    start_ids = sorted(start)
    hops = dict.fromkeys(start_ids, 0)
    frontier = start_ids
    for distance in range(1, max_hops + 1):
        nearer = []
        for source in frontier:
            for target, _probability in out.get(source, ()):
                if target not in hops:
                    hops[target] = distance
                    nearer.append(target)
        if not nearer:
            break
        frontier = nearer

    scores: dict[str, float] = {}
    residual = dict(start)
    sent: dict[str, dict[str, float]] = {}
    queue = deque(start_ids)
    queued = set(start_ids)
    residual_get = residual.get
    scores_get = scores.get
    sent_get = sent.get
    append = queue.append

    while queue:
        source = queue.popleft()
        queued.discard(source)
        mass = residual[source]
        if mass <= epsilon:
            continue
        residual[source] = 0.0
        scores[source] = scores_get(source, 0.0) + alpha * mass
        if hops[source] >= max_hops:
            continue
        row = out.get(source)
        if not row:
            continue
        spread = spread_share * mass
        for target, probability in row:
            amount = spread * probability
            total = residual_get(target, 0.0) + amount
            residual[target] = total
            senders = sent_get(target)
            if senders is None:
                sent[target] = senders = {}
            senders[source] = senders.get(source, 0.0) + amount
            if total > epsilon and target not in queued:
                queued.add(target)
                append(target)

    predecessor: dict[str, str] = {}
    unexplained: list[tuple[str, int]] = []
    for artist in sorted(sent):
        depth = hops[artist]
        if depth == 0:
            continue
        senders = sent[artist]
        best, best_amount = None, 0.0
        for sender in sorted(senders):
            if hops[sender] == depth - 1 and senders[sender] > best_amount:
                best, best_amount = sender, senders[sender]
        if best is None:
            unexplained.append((artist, depth))
        else:
            predecessor[artist] = best

    # An artist can be reached only by senders further out than itself; fall
    # back to its strongest edge from the previous hop, which BFS guarantees.
    if unexplained:
        incoming: dict[str, list[tuple[str, float]]] = {}
        for source in sorted(out):
            if source in hops:
                for target, probability in out[source]:
                    incoming.setdefault(target, []).append((source, probability))
        for artist, depth in unexplained:
            nearer = [
                (-probability, source)
                for source, probability in incoming.get(artist, ())
                if hops.get(source) == depth - 1
            ]
            if nearer:
                predecessor[artist] = min(nearer)[1]

    return WalkResult(scores=scores, hops=hops, predecessor=predecessor)


def reason_path(walk: WalkResult, artist_id: str) -> tuple[str, ...]:
    """The hop-by-hop path from a start artist to this one, or () if there is none."""
    hops = walk.hops
    if artist_id not in hops:
        return ()
    predecessor = walk.predecessor
    path = [artist_id]
    current = artist_id
    while True:
        depth = hops[current]
        if depth == 0:
            path.reverse()
            return tuple(path)
        nearer = predecessor.get(current)
        if nearer is None or hops.get(nearer, depth) != depth - 1:
            return ()
        path.append(nearer)
        current = nearer


def select_candidates(
    walk: WalkResult,
    seeds: UserSeeds,
    start: Mapping[str, float],
    config: GraphConfig = DEFAULT_GRAPH_CONFIG,
) -> list[tuple[str, float]]:
    """The best-scoring artists the user hasn't started from or judged already.

    Highest score first, ties broken by artist id.
    """
    excluded = set(start) | seeds.preferred() | seeds.removed(config)
    ranked = sorted(
        (
            (artist, score)
            for artist, score in walk.scores.items()
            if score > 0 and artist not in excluded
        ),
        key=lambda candidate: (-candidate[1], candidate[0]),
    )
    return ranked[: config.candidate_limit]
