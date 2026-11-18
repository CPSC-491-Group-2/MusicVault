"""Run the graph walk and the deck ranking on a sample or synthetic catalog.

Prints the walk candidates, the deck and a few sanity checks to stdout, and
timings to stderr, so stdout stays byte-identical between runs. From the
backend directory:

    PYTHONPATH=.:../spotify-api-backend python scripts/graph_walk_demo.py
    python scripts/graph_walk_demo.py --profile mixed --no-hub-damping
    python scripts/graph_walk_demo.py --synthetic
"""

from __future__ import annotations

import argparse
import json
import random
import statistics
import sys
import time
from collections import Counter
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.services.deck_ranking import (
    CatalogArtist,
    CatalogTrack,
    DeckConfig,
    check_variety,
    rank_deck,
)

from app.services.graph_walk import (
    ALGORITHM_VERSION,
    PROVIDERS,
    Edge,
    GraphConfig,
    UserSeeds,
    build_graph,
    personalized_pagerank,
    select_candidates,
    start_vector,
)
from app.services.similarity import TrackFeatures

SAMPLE = Path(__file__).resolve().parent / "data" / "graph_walk_sample.json"
RANK_RUNS = 5
RANK_TARGET_MS = 200

SYNTHETIC_SEED = 491
SYNTHETIC_ARTISTS = 5_000
SYNTHETIC_COMMUNITIES = 50
SYNTHETIC_EDGES = 50_000
SYNTHETIC_TRACKS_PER_ARTIST = 3
SYNTHETIC_INTRA_SHARE = 0.85


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--profile", default="indie", help="profile in the sample file")
    parser.add_argument(
        "--no-hub-damping",
        action="store_true",
        help="divide edge weights by 1 instead of log(2 + in-degree)",
    )
    parser.add_argument(
        "--synthetic",
        action="store_true",
        help="generate a 5,000 artist catalog instead of reading the sample",
    )
    parser.add_argument("--limit", type=int, default=20, help="deck size")
    args = parser.parse_args()

    if args.synthetic:
        run_synthetic(args)
    else:
        run_sample(args)


def run_sample(args: argparse.Namespace) -> None:
    data = json.loads(SAMPLE.read_text(encoding="utf-8"))
    if args.profile not in data["profiles"]:
        sys.exit(f"unknown profile {args.profile!r}: {sorted(data['profiles'])}")
    profile = data["profiles"][args.profile]
    artists = {artist["id"]: artist for artist in data["artists"]}

    edges = [
        Edge(edge["source"], edge["target"], edge["provider"], edge["score"])
        for edge in data["edges"]
    ]
    catalog_artists = [
        CatalogArtist(artist["id"], artist["fans"], artist["top_tag"])
        for artist in data["artists"]
    ]
    features = {track["id"]: sample_features(track) for track in data["tracks"]}
    catalog_tracks = [
        CatalogTrack(track["artist_id"], features[track["id"]])
        for track in data["tracks"]
    ]
    seeds = UserSeeds(
        saved_artists=frozenset(profile["saved_artists"]),
        top_track_artists=tuple(profile["top_track_artists"]),
        liked_artists=frozenset(profile["liked_artists"]),
        dislikes=dict(profile["dislikes"]),
    )
    seed_features = [features[track_id] for track_id in profile["seed_tracks"]]

    graph_config = GraphConfig(hub_damping=not args.no_hub_damping)
    deck_config = DeckConfig(graph=graph_config)
    graph, build_ms = timed(build_graph, edges, graph_config)
    start = start_vector(seeds, graph_config)
    walk = personalized_pagerank(graph, start, graph_config)
    candidates = select_candidates(walk, seeds, start, graph_config)
    deck, rank_ms = timed(
        rank_deck,
        graph,
        seeds,
        seed_features,
        catalog_artists,
        catalog_tracks,
        limit=args.limit,
        exclude=profile["exclude"],
        config=deck_config,
    )

    print(f"algorithm: {ALGORITHM_VERSION}")
    print(f"profile: {args.profile}")
    print(f"hub damping: {graph_config.hub_damping}")
    print(
        f"catalog: {len(catalog_artists)} artists, {len(edges)} edges, "
        f"{len(catalog_tracks)} tracks"
    )
    print(f"start artists: {', '.join(sorted(start)) or 'none'}")

    print("\nWalk candidates (top 10):")
    for rank, (artist_id, score) in enumerate(candidates[:10], start=1):
        artist = artists[artist_id]
        print(
            f"  {rank:2d}. {artist_id}  {artist['name']}  "
            f"[{artist['cluster']}]  {score:.6f}"
        )
    hub_rank = next(
        (
            rank
            for rank, (artist_id, _) in enumerate(candidates, start=1)
            if artists[artist_id]["cluster"] == "hub"
        ),
        None,
    )
    print(f"hub rank: {hub_rank}" if hub_rank else "hub rank: not a candidate")

    print(f"\nDeck (top {len(deck)}):")
    for position, item in enumerate(deck, start=1):
        artist = artists[item.artist_id]
        path = " -> ".join(artists[step]["name"] for step in item.reason_path)
        print(
            f"  {position:2d}. {item.track_id}  {artist['name']}  "
            f"[{artist['cluster']}]  score {item.score:.6f}  "
            f"graph {item.components['graph']:.6f}  "
            f"similarity {item.components['similarity']:.6f}  "
            f"discovery {item.components['discovery']:.6f}"
        )
        print(f"      reason: {path or 'cold start'}")

    print()
    report_variety(deck, catalog_artists, deck_config)
    if start:
        report_relevance(deck, artists, data["clusters"], start)
    report_forbidden(deck, seeds, start, deck_config, profile["exclude"])
    report_reasons(deck, start, deck_config)

    print(f"build_graph: {build_ms:.1f} ms", file=sys.stderr)
    print(f"rank_deck: {rank_ms:.1f} ms", file=sys.stderr)


def run_synthetic(args: argparse.Namespace) -> None:
    rng = random.Random(SYNTHETIC_SEED)
    artist_ids = [f"s{index:04d}" for index in range(SYNTHETIC_ARTISTS)]
    per_community = SYNTHETIC_ARTISTS // SYNTHETIC_COMMUNITIES
    community = {
        artist_id: index // per_community for index, artist_id in enumerate(artist_ids)
    }

    catalog_artists = [
        CatalogArtist(
            artist_id, rng.randint(500, 5_000_000), f"tag{community[artist_id]:02d}"
        )
        for artist_id in artist_ids
    ]
    edges = synthetic_edges(rng, artist_ids, community, per_community)
    features = {}
    catalog_tracks = []
    for artist_id in artist_ids:
        for number in range(1, SYNTHETIC_TRACKS_PER_ARTIST + 1):
            track = synthetic_features(rng, artist_id, community[artist_id], number)
            features[track.track_id] = track
            catalog_tracks.append(CatalogTrack(artist_id, track))

    picked = rng.sample(range(SYNTHETIC_COMMUNITIES), 2)
    pool = [artist_id for artist_id in artist_ids if community[artist_id] in picked]
    start_artists = rng.sample(pool, 10)
    seeds = UserSeeds(
        saved_artists=frozenset(start_artists[:5]),
        top_track_artists=tuple(start_artists[5:]),
    )
    seed_features = [features[f"t_{artist_id}_1"] for artist_id in start_artists]

    graph_config = GraphConfig(hub_damping=not args.no_hub_damping)
    deck_config = DeckConfig(graph=graph_config)
    graph, build_ms = timed(build_graph, edges, graph_config)
    start = start_vector(seeds, graph_config)
    walk = personalized_pagerank(graph, start, graph_config)
    candidates = select_candidates(walk, seeds, start, graph_config)

    runs = []
    for _ in range(RANK_RUNS):
        deck, elapsed = timed(
            rank_deck,
            graph,
            seeds,
            seed_features,
            catalog_artists,
            catalog_tracks,
            limit=args.limit,
            config=deck_config,
        )
        runs.append(elapsed)

    print(f"algorithm: {ALGORITHM_VERSION}")
    print("profile: synthetic")
    print(f"hub damping: {graph_config.hub_damping}")
    print(
        f"catalog: {len(catalog_artists)} artists, {len(edges)} edges, "
        f"{len(catalog_tracks)} tracks, {SYNTHETIC_COMMUNITIES} communities"
    )
    print(f"start artists: {', '.join(sorted(start))}")
    print(f"walk reached {len(walk.scores)} artists, {len(candidates)} candidates")

    print("\nDeck (first 10):")
    for position, item in enumerate(deck[:10], start=1):
        print(
            f"  {position:2d}. {item.track_id}  {item.artist_id}  "
            f"[c{community[item.artist_id]:02d}]  score {item.score:.6f}  "
            f"graph {item.components['graph']:.6f}  "
            f"similarity {item.components['similarity']:.6f}  "
            f"discovery {item.components['discovery']:.6f}"
        )

    print()
    report_variety(deck, catalog_artists, deck_config)
    top = deck[:10]
    near = sum(1 for item in top if community[item.artist_id] in picked)
    print(f"relevance: {near}/{len(top)} of top {len(top)} from the user's communities")
    report_forbidden(deck, seeds, start, deck_config, ())
    report_reasons(deck, start, deck_config)

    print(f"build_graph: {build_ms:.1f} ms", file=sys.stderr)
    print(
        f"rank_deck: best {min(runs):.1f} ms, median {statistics.median(runs):.1f} ms "
        f"(target < {RANK_TARGET_MS} ms)",
        file=sys.stderr,
    )


def synthetic_edges(rng, artist_ids, community, per_community) -> list[Edge]:
    pairs = {}
    while len(pairs) < SYNTHETIC_EDGES:
        source = rng.choice(artist_ids)
        if rng.random() < SYNTHETIC_INTRA_SHARE:
            first = community[source] * per_community
            target = artist_ids[rng.randrange(first, first + per_community)]
        else:
            target = rng.choice(artist_ids)
        if target == source or (source, target) in pairs:
            continue
        pairs[(source, target)] = (
            rng.choice(PROVIDERS),
            round(rng.uniform(0.3, 1.0), 3),
        )
    return [
        Edge(source, target, provider, score)
        for (source, target), (provider, score) in sorted(pairs.items())
    ]


def synthetic_features(rng, artist_id, community, number) -> TrackFeatures:
    return TrackFeatures(
        track_id=f"t_{artist_id}_{number}",
        artists=frozenset({artist_id}),
        genres=frozenset({f"tag{community:02d}", f"family{community % 7}"}),
        audio={
            "danceability": round(rng.uniform(0.2, 0.95), 3),
            "energy": round(rng.uniform(0.2, 0.95), 3),
            "valence": round(rng.uniform(0.1, 0.9), 3),
            "acousticness": round(rng.uniform(0.05, 0.9), 3),
            "tempo": round(rng.uniform(70, 160), 1),
        },
    )


def sample_features(track) -> TrackFeatures:
    return TrackFeatures(
        track_id=track["id"],
        artists=frozenset({track["artist_id"]}),
        genres=frozenset(genre.lower() for genre in track["genres"]),
        audio=dict(track["audio"]),
    )


def report_variety(deck, catalog_artists, config) -> None:
    by_id = {artist.artist_id: artist for artist in catalog_artists}
    violations = check_variety(deck, by_id, config)
    if violations:
        print("variety check: FAILED")
        for violation in violations:
            print(f"  {violation}")
    else:
        print("variety check: OK")


def report_relevance(deck, artists, clusters, start) -> None:
    counts = Counter(artists[artist_id]["cluster"] for artist_id in start)
    cluster = min(counts.items(), key=lambda item: (-item[1], item[0]))[0]
    allowed = {cluster, *clusters[cluster]["linked"]}
    top = deck[:10]
    near = sum(1 for item in top if artists[item.artist_id]["cluster"] in allowed)
    print(
        f"relevance: {near}/{len(top)} of top {len(top)} from {cluster} "
        "or linked clusters"
    )


def report_forbidden(deck, seeds, start, config, exclude) -> None:
    excluded = set(exclude)
    removed = seeds.removed(config.graph)
    preferred = seeds.preferred()
    problems = []
    for item in deck:
        if item.track_id in excluded:
            problems.append(f"{item.track_id} is excluded")
        if item.artist_id in start:
            problems.append(f"{item.track_id} is by start artist {item.artist_id}")
        if item.artist_id in preferred:
            problems.append(f"{item.track_id} is by rated artist {item.artist_id}")
        if item.artist_id in removed:
            problems.append(f"{item.track_id} is by removed artist {item.artist_id}")
    report("forbidden check", problems)


def report_reasons(deck, start, config) -> None:
    problems = []
    for item in deck:
        path = item.reason_path
        if not start:
            if path:
                problems.append(f"{item.track_id} has a reason path on a cold start")
            continue
        if not path:
            problems.append(f"{item.track_id} has no reason path")
        elif path[0] not in start:
            problems.append(f"{item.track_id} path starts at {path[0]}, not a seed")
        elif path[-1] != item.artist_id:
            problems.append(f"{item.track_id} path ends at {path[-1]}")
        elif len(path) - 1 > config.graph.max_hops:
            problems.append(f"{item.track_id} path is {len(path) - 1} hops")
    report("reason check", problems)


def report(label, problems) -> None:
    if problems:
        print(f"{label}: FAILED")
        for problem in problems:
            print(f"  {problem}")
    else:
        print(f"{label}: OK")


def timed(action, *args, **kwargs):
    start = time.perf_counter()
    result = action(*args, **kwargs)
    return result, (time.perf_counter() - start) * 1000


if __name__ == "__main__":
    main()
