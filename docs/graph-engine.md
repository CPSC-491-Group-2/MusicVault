# Graph Engine

MusicVault builds a deck of recommended tracks by walking an artist similarity graph outwards from the artists a user already shows a taste for, then ranking the tracks of the artists it reaches. The walk lives in `backend/app/services/graph_walk.py` and the ranking in `backend/app/services/deck_ranking.py`. Both are pure functions of their inputs (no database, HTTP, clock or randomness) and use only the Python standard library, so the same catalog and settings always give the same deck in the same order.

The graph answers "who is near the artists this user likes", which [similarity scoring](similarity-scoring.md) cannot: that scorer compares two songs directly, so it can only find songs that already look like the user's songs. The deck combines both — the graph picks the artists, the scorer picks their tracks.

Algorithm version: `graph-v1`. See [Version history](#version-history). Store it with every deck it produces, and bump it whenever a formula or default below changes.

## Inputs

| Input | Type | Notes |
|---|---|---|
| Edges | `Edge(source, target, provider, score)` | One provider's claim that `target` is similar to `source`. `score` is 0–1 |
| Seeds | `UserSeeds(saved_artists, top_track_artists, liked_artists, dislikes)` | What the user has saved, listened to most, rated up, and rated down. `dislikes` maps artist ID to a count |
| Artists | `CatalogArtist(artist_id, fans, top_tag)` | `fans` is a listener count, `None` when unknown. `top_tag` is the artist's main tag, `None` when unknown |
| Tracks | `CatalogTrack(artist_id, features)` | `features` is the `TrackFeatures` the similarity scorer uses; `track_id` reads through to it |
| Seed features | `Sequence[TrackFeatures]` | The user's own tracks in rank order, best first, for the similarity component |

Artists are identified by their MusicVault artist ID throughout, never by name. `top_track_artists` is in rank order (index 0 = the user's most played artist) and may repeat an artist that is also saved.

## Graph

### Providers

Each provider gets a weight λ, because they are not equally trustworthy:

| Provider | λ | What it is |
|---|---|---|
| `lastfm_similar` | 1.0 | Last.fm similar artists, derived from real listening behaviour, so it carries the most signal |
| `deezer_related` | 0.8 | Deezer related artists. Also behavioural, but tuned for a catalog rather than for taste |
| `mb_relation` | 0.6 | MusicBrainz artist relationships (same members, side projects). Factual rather than behavioural: related artists can sound nothing alike |
| `co_credit` | 0.5 | Two artists credited on the same track in our own data. The weakest signal, and the one most biased towards popular collaborators |

Edges whose provider is not in this list are ignored, as are self-loops. When the same `(source, target, provider)` arrives more than once, the highest score wins, so re-fetching a provider cannot inflate an edge.

### Edge weight

Every provider that reports a pair contributes, so a pair two providers agree on beats a pair only one reports:

```
raw_ij = Σ_p λ_p · s_ij^(p)        over providers p reporting i -> j
w_ij   = raw_ij / log(2 + indeg(j))
```

`indeg(j)` counts the **distinct sources** pointing at `j`, not the edges, so one source reporting the same pair through four providers still counts once. The logarithm is natural. With `hub_damping = False` the divisor is 1 and `w_ij = raw_ij`.

### Hub damping

Without damping, the walk ends up recommending whoever is popular. Every provider points thousands of artists at the handful everyone is "similar" to, so those hubs collect mass from every direction no matter where the walk started, and the deck turns into a chart. Dividing by `log(2 + indeg(j))` charges an artist for being pointed at from everywhere: an artist with 30 inbound sources keeps `1/3.47` of its raw weight, one with 4 keeps `1/1.79`. The log keeps that charge gentle, so a genuinely well-connected artist is damped, not erased.

This is a heuristic, not a correction for a known bias. It is a `GraphConfig` field so the effect stays measurable: the demo's sample graph has one deliberate hub, which ranks first among candidates with damping off and outside the top three with it on.

### Row normalization

Outgoing weights are normalized per artist, so a walk step is a probability distribution and an artist with many edges does not push out more mass than one with few:

```
p_ij = w_ij / Σ_k w_ik
```

## Start vector

The walk starts from the artists the user already shows a taste for. Saved artists count 1.0, and a top-track artist at rank `r` counts `top_track_decay ** r` (rank 0 = the user's top artist), so the artists they actually play most pull hardest. An artist that is both saved and played adds both contributions.

```
mass(a)  = 1.0 [if saved] + Σ top_track_decay ** r    over ranks r where top_track_artists[r] == a
start(a) = mass(a) / Σ mass(x)                        over artists x not removed
```

Artists with at least `dislike_threshold` (2) dislikes are dropped before normalizing, so the walk never starts from an artist the user has told us twice they do not want. A single dislike is not enough: one bad track is not a verdict on an artist.

If the user has no saved and no top-track artists, the start vector is empty and the deck falls back to [cold start](#cold-start).

## Walk

The walk is a personalized PageRank computed by local push (Andersen–Chung–Lang), not by power iteration over the whole graph: the user's taste touches a few hundred artists out of the whole catalog, and local push only ever visits those.

Each artist holds a settled score and a residual. Pushing an artist settles the restart share of its residual and spreads the rest along its normalized out-edges:

```
scores[u] += α · r[u]
r[v]      += (1 - α) · r[u] · p_uv      for each out-edge u -> v
r[u]       = 0
```

- `α` is `restart_probability`, 0.15. It is the share of a visit that ends at the artist instead of walking on, so a lower `α` reaches further.
- Artists are pushed while their residual is above `epsilon` (1e-4), from a FIFO queue seeded with the start artists in sorted ID order. Push order can only move scores by amounts on the order of `epsilon`; fixing it keeps the result identical between runs.
- `hops[u]` is the fewest steps from the start set to `u`. An artist at `max_hops` (3) settles `α · r[u]` and **drops** the rest, as does a dangling artist with no out-edges. So mass never travels more than three hops, and the deck can always be explained as a short path from something the user likes.

`WalkResult` carries `scores`, `hops`, and a `predecessor` for every artist the walk reached: the sender one hop closer to the start set that sent it the most mass, ties broken by the smallest ID, falling back to its strongest in-neighbour one hop closer when nothing was recorded. `reason_path(walk, artist_id)` follows those predecessors back to a start artist and returns the path, at most three hops, start artist first.

## Candidates

`select_candidates` takes the top `candidate_limit` (200) artists by walk score, sorted by `(-score, artist_id)`, after dropping:

- start artists, which the user already has;
- artists with any preference, liked or disliked, since the user has already judged them;
- removed artists (at least `dislike_threshold` dislikes), which the start vector dropped too.

A single dislike removes an artist from the deck even though it does not remove it from the start vector: it is enough of a signal not to recommend them again, but not enough to throw away their listening history.

## Deck score

Every track of every candidate artist is scored, and the graph, the similarity scorer and a discovery bonus are combined:

```
graph      = walk_score(artist) / max walk_score over candidates
similarity = the track's score from similarity.rank_candidates(seed_features, candidate tracks)
discovery  = 1 - discovery_penalty · fans_pct(artist)
score      = (graph_weight · graph + similarity_weight · similarity) · discovery
```

`graph` is divided by the best candidate's walk score, so it is always 0–1 whatever the absolute walk scores are: they depend on how many seeds the user has, and would otherwise make the two components incomparable. `similarity` is the same 0–1 score documented in [similarity scoring](similarity-scoring.md), with its own `ScoringConfig`.

Results are sorted by `(-score, track_id)`, so the order never depends on input order. Each `DeckItem` carries its `components` (`graph`, `similarity`, `discovery`) and the artist's `reason_path`, for showing the user why a card is there.

### Fans percentile

`fans_pct` is the artist's rank by fan count **within the catalog passed in**, 0 for the fewest fans and 1 for the most, with ties sharing the midrank:

```
fans_pct(a) = (count_less + (count_equal - 1) / 2) / (n - 1)
```

`count_less` is how many artists have fewer fans, `count_equal` how many have the same (including `a`), and `n` the number of artists. With one artist the result is 0. An artist whose fan count is unknown gets `unknown_fans_pct` (0.5) instead of being treated as unknown-is-tiny, which would hand the deck to artists we simply failed to look up.

A percentile is used rather than the raw count because fan counts span five orders of magnitude: any linear penalty on the raw number is either meaningless for small artists or fatal for everyone else.

### Defaults

| Component | Weight | Why |
|---|---|---|
| `graph` | 0.6 | The graph is what finds artists the user has never heard, which is the point of the deck |
| `similarity` | 0.4 | Keeps the cards inside the user's taste: the graph can reach an artist for structural reasons that has nothing in common with their songs |
| `discovery` | penalty 0.3 | A multiplier, not a weight: at most it cuts a card's score by 30%, so a well-known artist can still win on a strong match. MusicVault's goal is lesser-known music, not obscurity for its own sake |

## Variety

A deck that is right but repetitive is a bad deck. The deck is filled greedily: each slot takes the highest-ranked remaining item that breaks no rule, and the items it skips stay in line for later slots. An item skipped only to end a tag run therefore comes back a card or two later, instead of losing its place to a much weaker match:

- At most `max_tracks_per_artist` (2) tracks per artist.
- Never more than `max_same_tag_run` (3) consecutive cards whose artists share the same `top_tag`. Artists with no `top_tag` never form a run, since an unknown tag is not evidence of sameness.

`check_variety(items, artists, config)` re-checks a finished deck against the same rules and returns one message per violation, or an empty list when the deck is clean.

## Cold start

With an empty start vector there is no walk and no similarity to measure, so the deck is ordered by `fans_pct`, lowest first, ties broken by `track_id`: a new user gets the least-known music in the catalog rather than nothing. Artists with any preference and removed artists are still left out, excluded tracks are still removed, and the variety rules still apply.

Components are `graph` 0, `similarity` 0 and `discovery = 1 - discovery_penalty · fans_pct`, and `score` is `discovery` alone. `reason_path` is empty, since there is no path to show.

## Exclude and limit

`exclude` is a collection of track IDs removed before ranking — tracks the user has already been shown, saved or skipped. Excluding tracks rather than artists keeps an artist's other tracks eligible.

`limit` (20) caps the deck after ranking and variety. Variety drops items, so a deck can be shorter than `limit` when the candidates are too alike; it is never longer.

## Tunable parameters

### GraphConfig

Invalid values raise `ValueError` when the config is created.

| Parameter | Default | Allowed | Effect |
|---|---|---|---|
| `provider_weights` | see [Providers](#providers) | weights ≥ 0 | Which providers count, and how much. A provider missing from the mapping is ignored |
| `hub_damping` | `True` | bool | Divide edge weights by `log(2 + indeg)`. `False` makes the divisor 1 and lets hubs dominate |
| `top_track_decay` | 0.9 | (0, 1] | How much less each lower-ranked top-track artist counts. 1 counts them equally |
| `dislike_threshold` | 2 | ≥ 1 | Dislikes needed before an artist is dropped from the start vector |
| `restart_probability` | 0.15 | (0, 1) | Share of a visit that settles instead of walking on. Lower reaches further and costs more |
| `epsilon` | 1e-4 | > 0 | Residual below which an artist is not pushed. Larger is faster and coarser |
| `max_hops` | 3 | ≥ 1 | How far from the start set mass may travel. Also the longest reason path |
| `candidate_limit` | 200 | ≥ 1 | How many artists reach the ranking stage |

### DeckConfig

| Parameter | Default | Allowed | Effect |
|---|---|---|---|
| `graph_weight` | 0.6 | ≥ 0 | Weight of the walk score |
| `similarity_weight` | 0.4 | ≥ 0 | Weight of the similarity score |
| `discovery_penalty` | 0.3 | [0, 1] | How strongly well-known artists are pushed down. 0 turns discovery off |
| `unknown_fans_pct` | 0.5 | [0, 1] | Percentile used when an artist's fan count is unknown |
| `max_tracks_per_artist` | 2 | ≥ 1 | Cards one artist may fill |
| `max_same_tag_run` | 3 | ≥ 1 | Consecutive cards that may share a `top_tag` |
| `graph` | `DEFAULT_GRAPH_CONFIG` | `GraphConfig` | Runs the start vector, the walk and candidate selection while ranking. Build the graph with the same config |
| `scoring` | `DEFAULT_CONFIG` | `ScoringConfig` | Passed to the similarity scorer |

`graph` and `scoring` are nested configs rather than copied fields, so there is one place to change a parameter. `hub_damping` belongs to `GraphConfig` because `build_graph` applies it, so comparing damping means building the graph again, not re-ranking.

## Demo

`backend/scripts/graph_walk_demo.py` runs the whole pipeline on a hand-made catalog in `backend/scripts/data/graph_walk_sample.json`: 31 artists with made-up names in three clusters (indie, electronic, hip hop) plus one popularity hub that all 30 of the others point at, 498 edges, 105 tracks, and three listener profiles (`indie`, `mixed`, `empty`). From the `backend` directory:

```bash
PYTHONPATH=.:../spotify-api-backend python scripts/graph_walk_demo.py
```

The script also adds `backend` to `sys.path` itself, so it runs without `PYTHONPATH` too.

| Flag | Effect |
|---|---|
| `--profile NAME` | Which listener profile to run: `indie` (default), `mixed` or `empty` (cold start) |
| `--no-hub-damping` | Build the graph with `hub_damping=False`, to see the hub take over the deck |
| `--synthetic` | Generate 5,000 artists in 50 communities, 50,000 edges and 15,000 tracks from a fixed seed, instead of reading the sample |
| `--limit N` | Deck size, default 20 |

It prints the walk candidates, the deck with each card's components and reason path, and four checks: variety, relevance (how much of the top 10 comes from the user's own cluster or a linked one), that no card is a start, rated, removed or excluded item, and that every reason path starts at a start artist, stays within `max_hops` and ends at the card's artist.

Timings go to **stderr** only, so stdout stays byte-identical between runs and can be diffed:

```text
build_graph: 123.4 ms
rank_deck: best 45.6 ms, median 47.0 ms (target < 200 ms)
```

## Known limitations

- **Hub damping is a heuristic.** `log(2 + indeg)` was chosen for its shape, not fitted to data. It is worth re-checking against real Last.fm and Deezer edges once they are stored.
- **Dislikes only remove.** A disliked artist is dropped from the start vector and the candidates, but its neighbours are not pushed down, so the artists around a disliked one can still fill the deck.
- **Providers are weighted, not calibrated.** The λ values rank the sources by how much we trust them; they do not account for how differently each provider scales its own scores.
- **Cold start is popularity-only.** With no seeds the deck is just the least-known music in the catalog; it cannot be personalised at all until the user saves something or their top tracks arrive.
- **One reason per card.** `reason_path` is the single strongest path, so a card reached from several seeds looks as though it came from one.
- **Percentiles are catalog-relative.** `fans_pct` is computed over the artists passed in, so a deck built from a narrow catalog penalises its biggest artist as if it were a global star.
- **Fan counts and tags are sparse.** Both come from third-party lookups; unknown values fall back to `unknown_fans_pct` and to never forming a tag run, which weakens discovery and variety rather than breaking them.
- **The three-hop limit is a cliff.** An artist four hops out scores exactly 0, however strongly connected the path is.

## Version history

**graph-v1**
- First version: weighted multi-provider edge graph with hub damping, a start vector from saved and top-track artists, local-push personalized PageRank limited to three hops, and a deck score combining walk score, similarity and a discovery bonus, with per-artist and per-tag variety rules.
