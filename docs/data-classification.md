# MusicVault Data Classification Policy

| | |
|---|---|
| **Control ID** | C-1 |
| **Control name** | Data Classification and Inventory Verification |
| **SOC 2 criterion** | C1.1 — Confidentiality |
| **Owner** | Jacob Sii |
| **Applies to** | Every column in the MusicVault PostgreSQL database (`backend/DDL/`), and the credentials and session data listed in section 4 |
| **Database inventory** | [`data-classification-inventory.csv`](data-classification-inventory.csv) |
| **Enforced by** | [`backend/tests/security/test_data_classification.py`](../backend/tests/security/test_data_classification.py), `data-classification` job in [`docker-build.yml`](../.github/workflows/docker-build.yml) |
| **Assessment evidence** | [`docs/evidence/sprint4/data-classification/`](evidence/sprint4/data-classification/) |
| **Review** | Every pull request that changes the schema; full review once per sprint |

## 1. Purpose

MusicVault stores user profiles, Spotify account information, OAuth credentials, listening history, preferences and recommendations alongside public music metadata. This policy classifies that information by sensitivity, so that protections can be applied according to its level, and requires that new database fields are classified before they reach `master`.

## 2. Classification levels

Each field or asset gets exactly one level. When something could fit two levels, the higher one applies.

| Level | Definition | MusicVault examples | Handling requirement |
|---|---|---|---|
| **Restricted** | Secrets that grant access to an account or system. Exposure lets someone act as a user or as MusicVault. | Spotify access and refresh tokens, password hashes, database credentials, application secrets | Strictly controlled access, secure storage, never exposed in logs or API responses |
| **Confidential** | Data about an identifiable person: identifiers, contact details, profile data, and behavior or anything inferred from it. | User profiles, Spotify identifiers, listening history, user preferences, recommendations | Access restricted to authorized users |
| **Internal** | System data with no meaning outside MusicVault and no link to a person on its own. | Internal identifiers, non-sensitive application configuration, operational logs | Access limited according to operational requirements |
| **Public** | Data already published by Spotify or another provider. | Song titles, artist names, albums, public music charts | Suitable for public access |

Rules for common database cases:

- A column that identifies a user (`users.id` and every `user_id` foreign key) is Confidential, because it joins the row to a person.
- A foreign key to a Public or Internal row (`song_id`, `artist_id`, `chart_id`) is Internal.
- Row audit timestamps (`created_at`, `updated_at`, `generated_at`, `fetched_at`) are Internal.

## 3. Handling requirements in detail

| Requirement | Restricted | Confidential | Internal | Public |
|---|---|---|---|---|
| Returned in API responses | Never | Only to the user it belongs to | Only when needed | Yes |
| Written to logs, error messages or `__repr__` | Never | No (IDs allowed for debugging) | Yes | Yes |
| Protected at rest | Hashed (passwords) or encrypted at application level (tokens), on top of Supabase disk encryption | Supabase disk encryption | Supabase disk encryption | None needed |
| Sent over the network | TLS only | TLS only | TLS only | TLS preferred |
| In tests, fixtures and seed data | Synthetic values only | Synthetic values only | Any | Any |
| On account deletion | Deleted (`ON DELETE CASCADE`) | Deleted (`ON DELETE CASCADE`) | Deleted with its row | Kept |
| Committed to Git | Never (enforced by the gitleaks `secret-scan` job) | Never real values | Allowed | Allowed |

## 4. Inventory

### 4.1 Database fields

All 76 columns in the 11 tables of `backend/DDL/initial_schema.sql` are listed in [`data-classification-inventory.csv`](data-classification-inventory.csv), with a level, category and rationale for each. The CSV is the record CI checks against.

| Table | Restricted | Confidential | Internal | Public |
|---|---|---|---|---|
| `users` | `password_hash` | `id`, `email`, `display_name` | timestamps | |
| `spotify_accounts` | `access_token`, `refresh_token` | `user_id`, `spotify_account_id`, `spotify_user_id`, `display_name`, `email`, `scope` | `id`, `token_expires_at`, timestamps | |
| `user_preferences` | | `user_id`, `preference_type`, `rating` | `id`, `song_id`, timestamps | |
| `user_top_songs` | | `user_id`, `time_range`, `rank` | `id`, `song_id`, `fetched_at` | |
| `recommendations` | | `user_id`, `score`, `reason` | `id`, `song_id`, `algorithm_version`, `generated_at` | |
| `songs` | | | `id`, `popularity_source`, `audio_features_source`, timestamps | title, artist, album, IDs, ISRC, duration, explicit, popularity, audio features, URLs |
| `artists` | | | `id`, `genres_source`, `genres_fetched_at`, timestamps | `name`, `spotify_artist_id`, `genres` |
| `song_artists` | | | `song_id`, `artist_id` | `position` |
| `charts` | | | `id`, timestamps | `name`, `source`, `chart_date` |
| `chart_entries` | | | `id`, `chart_id`, `song_id`, `created_at` | `position` |

No tables are planned but unbuilt at the time of writing. A future table is classified in the same pull request that adds it (section 5).

### 4.2 Sensitive assets outside the database

| Asset | Level | Where it lives | Protection today |
|---|---|---|---|
| `SECRET_KEY` (signs the session cookie) | Restricted | Environment variable; GitHub Actions secret for deploys | Never committed; gitleaks scan |
| `DATABASE_URL` (includes the Supabase password) | Restricted | Environment variable; GitHub Actions secret for deploys | Never committed; gitleaks scan |
| `SPOTIFY_CLIENT_SECRET` | Restricted | Environment variable; GitHub Actions secret for deploys | Never committed; gitleaks scan |
| `SPOTIFY_ACCESS_TOKEN` (optional, for the Spotify integration tests) | Restricted | Developer's local environment only | Tests skip when it is unset |
| `GITHUB_TOKEN` (CI) | Restricted | Issued by GitHub per workflow run | Scoped by each workflow's `permissions` |
| Session cookie (carries the logged-in `user_id` and the OAuth `state`) | Restricted | User's browser | Signed with `SECRET_KEY`; `HttpOnly`, `SameSite=Lax`, `Secure` where served over HTTPS |
| Local `.env` files | Restricted | Developer machines | Gitignored; gitleaks scan |
| `SPOTIFY_CLIENT_ID`, `SPOTIFY_REDIRECT_URI`, `SPOTIFY_SCOPES`, `FRONTEND_URL`, `FLASK_DEBUG`, `SESSION_COOKIE_SECURE` | Internal | Environment variables | Non-sensitive configuration |
| CI test database credentials (`musicvault`/`musicvault`) | Internal | `docker-build.yml` | Throwaway Postgres container, deleted after each run |
| Application and CI logs | Internal | Hosting provider; GitHub Actions | Must not contain Restricted or Confidential values (section 3) |

## 5. Procedure for adding or changing a field

1. Choose a level from section 2.
2. Add the column to `backend/DDL/initial_schema.sql` (and a migration if Supabase needs one).
3. Add a row to `data-classification-inventory.csv` with the table, column, level, category and a one-line rationale.
4. If the table has a SQLAlchemy model, label the column with `info=classified(DataClass.<LEVEL>)` from `models/classification.py`.
5. Open a pull request. The `data-classification` CI job must pass before merge, and the reviewer checks that the level matches section 2.

Removing a column also removes its inventory row; the test fails if the inventory lists a column that no longer exists. A new credential or secret outside the database is added to section 4.2 in the pull request that introduces it.

## 6. Automated enforcement

`test_data_classification.py` runs in GitHub Actions on every pull request and push to `master`, both in its own `data-classification` job and as part of `backend-tests`. It fails when:

- a SQLAlchemy model column has no classification, or one that is not a level in section 2 (completeness);
- a model column's label differs from its inventory row, or a model column is missing from the inventory (accuracy);
- a known sensitive field, such as a token, password hash or email, is not at its required level (accuracy);
- a column in the schema built from the DDL has no inventory row, or the inventory lists a column the schema doesn't have (completeness for tables without a model, such as `recommendations` and `charts`).

The test also checks itself: it builds a model with an unlabeled column and confirms the validator reports it.

It also checks part of section 3 against the classifications, failing when:

- a model's `__repr__` (which logs and tracebacks print) shows a Confidential or Restricted value; keys are allowed;
- a response schema declares a field named after a Restricted column, or `/users/<id>` or `/me` returns a Restricted value;
- a database error message contains a statement's bound values (the engine sets `hide_parameters=True`, because routes log database errors with `logger.exception`);
- Spotify access or refresh tokens are stored as the plaintext value. This check is marked as an expected failure (`xfail(strict=True)`) until application-level encryption is built (section 7); once tokens are encrypted, the marker must be removed or the job fails.

Password hashing is not yet built (local registration and login return 503), so nothing writes `users.password_hash` today and its hashing requirement can't be tested yet.

The automated checks prove that every field has a level. Whether the level is the right one is checked by the pull request reviewer against section 2. Log statements are reviewed by hand, because no test can tell which variables a log line prints.

## 7. Exceptions

An exception (for example, a Restricted field that cannot yet meet section 3) is recorded as a Jira work item that names the field, the unmet requirement and the planned fix. Open exceptions are listed in the current assessment document.

| Field | Unmet requirement | Planned fix | Jira |
|---|---|---|---|
| `spotify_accounts.access_token`, `spotify_accounts.refresh_token` | Encrypted at application level | Encrypt with a key held as a deployment secret; migrate existing rows | `<ticket>` |

## 8. Revision history

| Date | Change | Author |
|---|---|---|
| 2026-11-02 | First version; all 76 existing columns and the non-database assets in section 4.2 classified | Jacob Sii |
| 2026-11-02 | Automated checks for section 3 handling (`__repr__`, database errors, API responses, token storage); token encryption exception recorded | Jacob Sii |
