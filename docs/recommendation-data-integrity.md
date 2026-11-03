# Recommendation Data Integrity

How the data feeding the recommendation engine is stored, selected and tested. The scoring itself is described in [similarity-scoring.md](similarity-scoring.md).

## Preferences

`backend/db/queries/preferences.py` reads and writes `user_preferences`, one row per user and song:

| Function | Behavior |
|---|---|
| `set_preference(db, user_id, song_id, type, rating=None)` | Creates the preference, or replaces the type and rating if the user already has one for that song |
| `save_preferences(db, user_id, entries)` | Sets several in one transaction, all or nothing. A song repeated in the batch keeps its last entry |
| `get_preference(db, user_id, song_id)` | One preference, or `None` |
| `get_preferences(db, user_id, types=None)` | A user's preferences, optionally only some types, oldest first |
| `delete_preference(db, user_id, song_id)` | Removes one; `False` if there wasn't one |

Types are `liked`, `disliked`, `saved`, `skipped` and `neutral`; ratings are optional integers 1–5.

- **Duplicates:** every write is one `INSERT ... ON CONFLICT (user_id, song_id) DO UPDATE`. Repeated submissions update the same row, and concurrent ones can't race each other into a duplicate or an error.
- **Invalid input** (unknown type, bad rating, missing song ID) raises `ValueError` before anything is written. The database's own constraints reject the same values if code bypasses these functions.
- **Unknown users or songs** raise `IntegrityError`, and the whole batch is rolled back.
- **Deletes:** deleting a user or a song removes its preferences. Other users' rows and the songs themselves are kept.

## Recommendation inputs

`get_recommendation_inputs(db, user_id, time_range)` in `backend/db/queries/recommendations.py` returns what the ranker needs:

- **Seeds:** the user's top songs for the time range in rank order, then their `liked` and `saved` songs, highest rating first (unrated last). A song is a seed once, in its first position.
- **Candidates:** every other song, ordered by song ID.
- Songs the user marked `disliked` or `skipped` are in neither list, even if they are top songs. `neutral` changes nothing.
- Each song's artist credits and artists are loaded with it, so converting them with `track_features_from_song` runs no further queries.

A user with no top songs or preferences gets no seeds, and every song as a candidate; the ranker then scores them all 0.

## Tests

| Work item | Tests |
|---|---|
| Preference creation and retrieval | `test_preference_queries.py`: creating, reading, filtering, deleting |
| Duplicate preference handling | Setting again updates the same row; repeated identical writes; repeats within a batch; a duplicate row written directly is rejected by the database |
| User/song/preference foreign-key integrity | Unknown user or song rejected; deleting a user or song cascades to its preferences only; preferences stay with their user |
| Missing or nullable song metadata | `test_recommendation_inputs.py`: songs with only required fields, malformed stored genres and audio values, the dataset's incomplete songs |
| Recommendation candidate queries | Seeds in rank order, candidates in ID order, liked/saved/disliked/skipped/neutral handling, other users' preferences ignored, empty catalog, unknown user, invalid time range |
| Recommendation inputs against controlled fixtures | The recommendation dataset is saved to the database; features read back must equal the in-memory fixtures, and every profile's ranking must match `recommendation_expected.json` |
| Failed transaction rollback | A batch failing on its last entry keeps neither its updates nor its new rows; a failed batch for an unknown user leaves nothing |
| Repeated/concurrent preference submissions | 12 threads submitting different preferences for one song at once leave one complete row; concurrent writes for different songs, and from different users, all land |
| Performance baseline | Query count must stay the same as the catalog grows (no per-song queries); timings below |

The database tests need Postgres, as described in the README's [Running Backend Tests](../README.md#running-backend-tests). `test_recommendation_inputs.py` also carries the `recommendation` marker. The `recommendation-tests` CI job has no database, so it skips these; `backend-tests` runs them against Postgres.

The fixed dataset is shared through `backend/tests/recommendation_fixtures.py`, which builds it either in memory or in the database with the same UUIDs.

## Performance baseline

Measured with `backend/scripts/benchmark_recommendation_queries.py` on 2026-11-02 (Apple M5, PostgreSQL 16.2, local socket connection). The user has 50 top songs and 20 liked songs; each song credits 2 artists and has 5 audio features. Each value is the median of 5 runs in milliseconds, with the range in brackets.

| Songs | Load inputs | Build features | Rank (top 50) | Total | Set 1 preference | Save 20 preferences |
|---|---|---|---|---|---|---|
| 1,000 | 38.5 (25.8–39.3) | 3.3 (3.1–3.4) | 181.6 (179.6–184.1) | 221.7 (210.2–225.9) | 0.4 (0.3–0.8) | 4.3 (4.2–4.4) |
| 5,000 | 238.8 (174.7–272.6) | 19.9 (19.3–42.9) | 963.4 (960.3–1009.4) | 1,223.8 (1,177.8–1,268.2) | 0.5 (0.4–1.0) | 4.4 (4.1–4.6) |
| 20,000 | 1,266.1 (1,040.7–1,311.8) | 79.5 (73.5–183.1) | 3,916.7 (3,888.4–4,038.2) | 5,278.0 (5,007.8–5,365.9) | 0.5 (0.4–1.2) | 4.5 (4.4–4.7) |

Findings:

- **Preference writes don't slow down as the catalog grows.** They go through the unique index on (user, song).
- **Loading inputs is linear in catalog size**, because every song is a candidate. The number of queries is fixed (checked by `test_query_count_does_not_grow_with_the_catalog`).
- **Ranking is the bottleneck**: it compares every candidate with every seed, so 20,000 songs × 70 seeds takes about 4 seconds. Before the catalog reaches that size, narrow the candidates in the query (for example, songs sharing an artist or genre with the seeds) or precompute recommendations in the background and store them in `recommendations`.

To re-run it (it rolls back everything it writes):

```bash
cd backend
PYTHONPATH=.:../spotify-api-backend python scripts/benchmark_recommendation_queries.py
```

Record the date, hardware and results here when the queries or the ranker change.
