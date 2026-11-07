# Similarity Scoring

MusicVault ranks candidate songs by how similar they are to a user's top songs. The scoring lives in `backend/app/services/similarity.py`. It is a pure function of its inputs (no database, clock or randomness), so the same songs and settings always give the same scores in the same order.

Algorithm version: `similarity-v2`. See [Version history](#version-history). Store it in `recommendations.algorithm_version` with every score it produces, and bump it whenever a formula or default below changes.

## Inputs

Each song is described by a `TrackFeatures`:

| Field | Source today | Notes |
|---|---|---|
| `artists` | `song_artists` → `artists.id` | Matched on artist ID, never on name, so "Tyler, The Creator" is one artist |
| `genres` | Union of the song's artists' `artists.genres` | Lowercased and trimmed. Not filled yet; see [Data sources](#data-sources) |
| `audio` | `songs.audio_features` | Numeric values only. Not filled yet |
| `popularity` | `songs.popularity` | Spotify no longer returns it in Development Mode |

`track_features_from_song(song)` builds one from a `Song` whose `artist_credits` are loaded.

An empty set or dict means **unknown**, not "none". Components with unknown data are left out of the score instead of counting as 0.

## Components

Each component compares two songs and returns a value from 0 (nothing alike) to 1 (identical), or `None` when either song lacks that data.

### Artist and genre

Jaccard overlap: shared items divided by all items.

```
overlap(A, B) = |A ∩ B| / |A ∪ B|
```

Examples: `{x}` vs `{x}` = 1. `{x, y}` vs `{y, z}` = 1/3. A song featuring an artist from the other song scores partially rather than 0.

### Audio

The mean scaled difference over the audio features both songs have, subtracted from 1. Audio is only compared when the two songs share at least `min_audio_features` (default 3) of the features below; with fewer, one or two numbers would decide the whole component.

```
distance(f) = min(|a_f - b_f| / range_f, 1)
audio       = 1 - mean(distance(f) for f in features both songs have)
```

| Feature | Range | Meaning |
|---|---|---|
| `danceability`, `energy`, `valence`, `acousticness` | 0.5 | Reported on a 0–1 scale. Real songs mostly sit in the middle of it, so a full 1.0 range made almost every pair score 0.75–0.90; with 0.5, a difference of half the scale counts as completely different |
| `tempo` | 60 BPM | A gap of 60 BPM or more counts as completely different |

Features outside this list (for example `loudness` or `key`) are ignored. NaN, infinite, boolean and non-numeric values are skipped. Half-time and double-time tempos (60 vs 120 BPM) are treated as different; this is a known limitation of v1.

## Combined score

A weighted mean of the components that have data:

```
score = Σ w_c · s_c / Σ w_c      over components c where s_c is not None and w_c > 0
```

If no component has data, the score is 0. This pairwise score leaves out any component either song lacks; ranking treats a candidate's missing data more strictly (see [Ranking](#ranking)). Scores are always between 0 and 1, which satisfies the `recommendations.score >= 0` constraint.

### Default weights

| Component | Weight | Why |
|---|---|---|
| Artist | 0.35 | The most precise signal, but narrow: on its own it only finds songs by artists the user already knows |
| Genre | 0.35 | Broader than artist, so it surfaces new artists in familiar styles, which supports MusicVault's goal of recommending lesser-known songs |
| Audio | 0.30 | Captures feel (energy, tempo, mood) across genres, but comes from a third-party source whose coverage and accuracy still need checking |

Only the ratios matter: weights of 0.7/0.7/0.6 score the same as the defaults. Because missing components are left out, a song with only artist data is scored on artists alone (weight rescaled to 1), not penalised for missing genres.

## Ranking

`rank_candidates(seeds, candidates)` ranks candidates against the user's top songs (`seeds`, best first):

1. Each candidate is compared with every seed.
2. Each component is averaged across seeds, with seed `i` (0 = the user's #1 song) weighted `seed_rank_decay ** i`.
   - If the **seed** lacks the component's data, that seed is skipped for it, so it doesn't dilute the average.
   - If the seed has the data but the **candidate** doesn't, the component scores `missing_data_score` (default 0). Otherwise a candidate with almost no data would be scored only on what little it has, and could outrank real matches.
   - If neither has it, the component is left out entirely. Until genres are fetched for any song, genre drops out for everyone, so nobody is penalised.
3. The averaged components are combined with the weights above.
4. If `popularity_penalty` is set and the candidate's popularity is known, the score is multiplied by `1 - popularity_penalty × popularity / 100`.
5. Candidates that are already seeds, and repeated candidates, are dropped.
6. Results are sorted by score, highest first. Ties are broken by `track_id`, so the order never depends on input order.

Each result carries a `reason`: the component with the largest weighted value (`artist`, `genre` or `audio`; earlier ones win ties), or `None` if nothing matched. It is meant for `recommendations.reason`.

## Tunable parameters

All are fields of `ScoringConfig`; invalid values raise `ValueError` when the config is created.

| Parameter | Default | Allowed | Effect |
|---|---|---|---|
| `artist_weight` | 0.35 | ≥ 0 | Weight of the artist component |
| `genre_weight` | 0.35 | ≥ 0 | Weight of the genre component |
| `audio_weight` | 0.30 | ≥ 0 | Weight of the audio component. At least one weight must be positive |
| `seed_rank_decay` | 0.9 | (0, 1] | How much less each lower-ranked seed counts. 1 counts all seeds equally |
| `popularity_penalty` | 0.0 | [0, 1] | How strongly popular songs are pushed down. 0 turns it off |
| `audio_feature_ranges` | see [Audio](#audio) | ranges > 0 | Which audio features are compared, and the difference that counts as completely different |
| `min_audio_features` | 3 | ≥ 1 | Shared audio features needed before audio is compared |
| `missing_data_score` | 0.0 | [0, 1] | Component score when ranking and the seed has data the candidate lacks. 0 treats it as no match |

## Data sources

| Data | Where it comes from | Status |
|---|---|---|
| Artists | Spotify track objects (`artists[].id`), saved by `save_top_songs` | Stored |
| ISRC | Spotify `external_ids.isrc`, saved to `songs.isrc` | Stored; used to look songs up in other databases |
| Genres | Spotify `GET /artists/{id}` if Development Mode still returns `genres`; otherwise Last.fm artist tags or MusicBrainz | Not fetched yet. Record the provider in `artists.genres_source` |
| Audio features | Spotify's `/audio-features` returns 403 for apps created after Nov 27, 2024. ReccoBeats accepts Spotify track IDs | Not fetched yet. Record the provider in `songs.audio_features_source` |

Until genres and audio features are fetched, scores are based on artist overlap only.

## Automated tests

| File | What it covers |
|---|---|
| `backend/tests/test_similarity.py` | Each component and the combined score on small hand-made examples, config validation, ranking rules, and building features from `Song` rows |
| `backend/tests/test_recommendation_regression.py` | The whole pipeline on a fixed dataset: `Song`/`Artist` rows → `track_features_from_song` → `rank_candidates` |
| `backend/tests/data/recommendation_dataset.json` | Made-up artists, songs and listener profiles (indie, hip-hop, mixed, sparse, malformed, empty), including deliberately missing and malformed metadata |
| `backend/tests/data/recommendation_expected.json` | The expected ranking for every profile: order, scores, reasons and components |

The regression tests check two things:

- **Snapshot:** every profile's ranking must match `recommendation_expected.json` exactly (scores rounded to 6 decimals). Any change in recommendation behaviour fails.
- **Behaviour:** checks that hold whatever the exact numbers are, for example "the indie listener's top 3 are indie songs", "a song with no metadata scores 0 instead of erroring", "shuffling the candidates doesn't change the result". A regenerated snapshot can't hide a regression in these.

Both test files carry the `recommendation` marker. The `recommendation-tests` job in `.github/workflows/docker-build.yml` runs them as their own check on every PR (`backend-tests` runs them too), so a recommendation regression shows up as a named failed check.

Run them locally from `backend`:

```bash
PYTHONPATH=.:../spotify-api-backend python -m pytest -m recommendation
```

When a change to recommendations is **intended**, regenerate the snapshot, check the new rankings make sense, and commit the file with the change, so reviewers can see exactly what moved in the PR diff:

```bash
UPDATE_RECOMMENDATION_SNAPSHOT=1 PYTHONPATH=.:../spotify-api-backend python -m pytest tests/test_recommendation_regression.py
```

Bump `ALGORITHM_VERSION` with any intended change; the snapshot records it and fails if they don't match.

## Version history

**similarity-v2**
- Audio needs at least 3 shared features (`min_audio_features`).
- The 0–1 audio features use a 0.5 range instead of 1.0, so styles are easier to tell apart.
- When ranking, a component the seed has but the candidate lacks scores `missing_data_score` (0) instead of being left out.
- Why: the regression dataset showed songs with one usable audio feature outranking real matches (for the indie listener, three such songs ranked 2nd–4th, ahead of a genuine indie match), and audio scoring nearly every pair 0.75–0.90.

**similarity-v1**
- First version: artist, genre and audio components, weighted mean over the components with data.

## Baseline recommendation quality review checklist

Run this review whenever the weights, formulas or data sources change, and record the result with the algorithm version.

**Setup**

- [ ] Pick at least 3 test users with different tastes (e.g. one narrow-genre listener, one broad listener, one with mostly lesser-known artists).
- [ ] Note what data each user's seeds and candidates have: artists only, artists + genres, or all three.
- [ ] Record the `algorithm_version` and any non-default `ScoringConfig` values.

**Relevance**

- [ ] At least 7 of each user's top 10 recommendations are songs the user, or a reviewer who knows their taste, would plausibly enjoy.
- [ ] No recommendation is a song already in the user's top songs.
- [ ] Each `reason` matches why the song looks similar (e.g. `artist` results share an artist with a seed).

**Variety and discovery**

- [ ] The top 10 is not dominated by one artist (no more than 3 songs by the same artist).
- [ ] At least a few recommendations are by artists not in the user's seeds, once genre or audio data is available.
- [ ] If `popularity_penalty` is on, less popular songs move up without irrelevant songs entering the top 10.

**Robustness**

- [ ] Songs missing genres or audio features still get sensible scores from the data they have.
- [ ] A user with very few seeds (1–3 songs) still gets recommendations.
- [ ] Running the ranking twice on the same data gives the same order.
- [ ] Re-ordering the candidate list does not change the results.

**Sign-off**

- [ ] Note any recommendations that looked wrong and which component caused them.
- [ ] Decide whether the defaults stay, or record new values and bump the algorithm version.
