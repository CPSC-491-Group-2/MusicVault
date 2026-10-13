# MusicVault

MusicVault is a CPSC 491 Senior Capstone project focused on helping users discover music based on their listening preferences. The goal of the application is to use user-selected music and Spotify data to generate personalized recommendations, including lesser-known or less-mainstream songs.

## Team Members

- Anjelo Go
- Frank Rangel
- Jacob Sii
- Marcus Martin
- Minh Nguyen

## Project Goals

MusicVault aims to provide users with a personalized music discovery experience. Planned features include:

- User account and profile management
- Spotify account integration
- Retrieval and storage of music data
- Manual song and preference input
- Personalized song recommendations
- Recommendation results and music insights
- CSV export functionality
- Music analytics and visualizations
- Responsive web interface

## Technology Stack

### Frontend

- Next.js
- React
- TypeScript
- oxlint

### Backend

- Python
- Flask
- Flask-CORS
- Black
- Ruff

### Additional Technologies

- PostgreSQL
- SQLAlchemy
- Spotify Web API
- GitHub
- Jira

The architecture and individual technologies may be adjusted as the team evaluates the existing MusicVault prototype and continues development.

## Current Development Status

### Sprint 1: Project Foundation and Architecture

Current work includes:

- Auditing the existing MusicVault repository
- Establishing the frontend and backend project structure
- Verifying frontend-to-backend communication
- Designing the initial PostgreSQL database structure
- Researching Spotify API capabilities
- Configuring development and deployment tooling
- Finalizing the semester implementation plan

## Repository Workflow

All development work should be completed on a separate branch.

Typical workflow:

1. Pull the latest version of the `master` branch.
2. Create a branch for the assigned Jira task.
3. Make and test changes on that branch.
4. Commit and push the branch to GitHub.
5. Open a Pull Request.
6. Have another team member review the Pull Request.
7. Merge approved changes into `master`.

Code should not be pushed directly to `master`.

## Repository Structure

```text
MusicVault/
├── backend/
│   ├── app/
│   │   ├── errors/
│   │   │   ├── __init__.py
│   │   │   └── handlers.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   └── health.py
│   │   ├── __init__.py
│   │   └── config.py
│   ├── run.py
│   ├── requirements.txt
│   └── pyproject.toml
│
├── frontend/
│   ├── app/
│   │   ├── library/
│   │   ├── profile/
│   │   ├── search/
│   │   ├── layout.tsx
│   │   └── page.tsx
│   ├── components/
│   │   ├── HealthStatus.tsx
│   │   └── Navbar.tsx
│   ├── services/
│   │   └── api.ts
│   └── types/
│       └── api.ts
│
├── database/
├── docs/
├── .gitignore
└── README.md
```

The repository structure may change as MusicVault development continues.

## Environment Variables

Configuration and secrets are read from environment variables. Copy the template at the repository root and fill it in:

```bash
cp .env.example .env
```

`.env` is gitignored. Never commit real secrets, and never put them in `compose.yml`, a Dockerfile, or source code.

| Variable | Required | Description |
|---|---|---|
| `SECRET_KEY` | For login | Signs the session cookie. Use a long random value (see below). |
| `SPOTIFY_CLIENT_ID` | For login | Client ID from the Spotify Developer Dashboard. |
| `SPOTIFY_CLIENT_SECRET` | For login | Client secret from the Spotify Developer Dashboard. Only the backend uses it. |
| `SPOTIFY_REDIRECT_URI` | For login | Callback URL. Must exactly match one registered in the Spotify dashboard. |
| `FRONTEND_URL` | No | Where users land after login, and the allowed CORS origin. Defaults to `http://localhost:3000`. |
| `SESSION_COOKIE_SECURE` | No | Set to `True` when the site is served over HTTPS. Defaults to `False`. |
| `DATABASE_URL` | No | PostgreSQL connection string. Defaults to a local `musicvault` database. |
| `TEST_DATABASE_URL` | Tests only | Database the backend tests use. Must end in `_test`. Defaults to a local `musicvault_test` database. See [Running Backend Tests](#running-backend-tests). |

Generate a `SECRET_KEY`:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

The backend reads `.env` automatically when started with `python run.py`. Docker Compose reads the same file and passes the values to the backend container, so they never end up in the image.

If the Spotify variables or `SECRET_KEY` are missing, the rest of the backend still runs, and the login routes return `503 Service Unavailable`.

### Production Values

Production does not use a `.env` file. The values are shared through the repository's `production` GitHub environment, under **Settings > Environments > production**, and the Deploy workflow passes them to Docker Compose when it starts the containers.

Add these as environment **secrets**:

| Secret | Description |
|---|---|
| `SECRET_KEY` | A different value from the one used locally. |
| `DATABASE_URL` | Connection string for the production database. |
| `SPOTIFY_CLIENT_ID` | Client ID of the Spotify app used in production. |
| `SPOTIFY_CLIENT_SECRET` | Client secret of that same app. |

Add these as environment **variables**, since they are not sensitive:

| Variable | Description |
|---|---|
| `FRONTEND_URL` | Public URL of the deployed site. |
| `SPOTIFY_REDIRECT_URI` | Production callback URL. Register it in the Spotify dashboard too. |
| `SESSION_COOKIE_SECURE` | `True` once the site is served over HTTPS. |

All seven are required. Deploy stops before pulling images if any of them is missing, rather than shipping a build whose login is quietly broken. Secrets are masked in the workflow logs and are never written to the runner's disk.

## Spotify Login Setup

MusicVault signs users in with Spotify using the OAuth authorization code flow.

1. Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard) and create an app (or ask a teammate for access to the team's app).
2. In the app settings, add this redirect URI:

   ```text
   http://127.0.0.1:3000/api/auth/spotify/callback
   ```

3. Copy the client ID and client secret into `.env`, and set:

   ```text
   SPOTIFY_REDIRECT_URI=http://127.0.0.1:3000/api/auth/spotify/callback
   FRONTEND_URL=http://127.0.0.1:3000
   ```

4. Start the backend and frontend, then open `http://127.0.0.1:3000` and click **Log in with Spotify**.

Use `127.0.0.1`, not `localhost`, everywhere. Spotify does not accept `localhost` redirect URIs, and the login session cookie is tied to the exact host, so opening the site on `localhost` would lose it partway through login.

Spotify apps start in Development Mode, where only users added under **User Management** in the dashboard can log in.

### How login works

| Endpoint | Description |
|---|---|
| `GET /api/auth/spotify/login` | Redirects the user to Spotify to approve access. |
| `GET /api/auth/spotify/callback` | Spotify redirects back here. The backend finishes login and redirects to `FRONTEND_URL`. |
| `POST /api/auth/spotify/logout` | Ends the session. Returns `204 No Content`. |

- **State/CSRF protection:** `/login` generates a random `state` value and stores it in a signed, HttpOnly session cookie. `/callback` only continues if Spotify returns the same value. Each `state` can be used once.
- **Client secret:** used only in the backend's server-to-server request to Spotify. It is never sent to the browser.
- **Redirect URI:** always taken from `SPOTIFY_REDIRECT_URI`, never from the request.
- **Accounts** are matched by Spotify user ID, not email, since Spotify does not guarantee that emails are verified.

If login fails, the user is sent back to the frontend with an `auth_error` query parameter:

| `auth_error` | Meaning |
|---|---|
| `access_denied` | The user declined on Spotify's consent screen. |
| `invalid_state` | The `state` was missing, wrong, or already used. Starting login again fixes it. |
| `spotify_error` | Spotify returned an error or could not be reached. |

### Protected routes

Routes that need a logged-in user use the `login_required` decorator from `app/auth.py`. It reads the user from the signed session cookie set at login, and the view can use that user as `g.current_user`. Anything else gets `401 Unauthorized`:

```json
{
  "error": "Unauthorized",
  "message": "You must be logged in to access this resource."
}
```

This includes a missing, unsigned, or tampered cookie, and a session for a user that has since been deleted.

| Endpoint | Description |
|---|---|
| `GET /api/v1/me` | Returns the logged-in user. |
| `GET /api/v1/users/{id}` | Returns the user only if `{id}` is the logged-in user. Any other ID gets `403 Forbidden`, including IDs that don't exist, so the route can't be used to discover accounts. |

On a flask-smorest `MethodView`, protect every method with `decorators = [login_required]`.

## Running the Backend

Navigate to the backend directory:

```bash
cd backend
```

Create a Python virtual environment:

```bash
python -m venv venv
```

Activate the virtual environment on Windows:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the Flask server:

```bash
python run.py
```

The backend runs at:

```text
http://127.0.0.1:5000
```

## Running the Frontend

Open another terminal and navigate to the frontend directory:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the Next.js development server:

```bash
npm run dev
```

The frontend runs at:

```text
http://localhost:3000
```

## API

MusicVault uses a REST API provided by the Flask backend.

API endpoints are versioned under:

```text
/api/v1
```

### Health Check

```text
GET /api/v1/health
```

Successful API responses use JSON.

Example response:

```json
{
  "service": "MusicVault API",
  "status": "ok"
}
```

The frontend maintains TypeScript interfaces for expected API responses in:

```text
frontend/types/api.ts
```

Backend and frontend changes to an API response should be updated together to keep the API contract synchronized.

### Error Format

API errors use a consistent JSON structure:

```json
{
  "error": "Not Found",
  "message": "The requested resource was not found."
}
```

## OpenAPI Documentation

The Flask backend provides interactive OpenAPI documentation through Swagger UI.

Start the backend:

```bash
cd backend
python run.py
```

With the backend running, Swagger UI is available at:

```text
http://127.0.0.1:5000/docs
```

The API is versioned under:

```text
/api/v1
```

Example endpoint:

```text
GET /api/v1/health
```

The OpenAPI schema is generated from the Flask routes and Marshmallow schemas.

API response schemas are defined in the Flask backend, and corresponding TypeScript interfaces are maintained in:

```text
frontend/types/api.ts
```

Backend and frontend API changes should be updated together to keep the API contract synchronized.

## Running Backend Tests

The backend tests run against a separate PostgreSQL test database, never the development database. The test database name must end in `_test`, or pytest will refuse to run.

Install the test dependencies:

```bash
cd backend
pip install -r requirements-dev.txt
```

You only need a running PostgreSQL server. Run the tests from the `backend` directory:

```bash
python -m pytest
```

There's no manual database setup. On each run, pytest:

1. Creates the test database if it doesn't exist yet.
2. Drops all its tables and rebuilds them from `DDL/initial_schema.sql`, so leftovers from an earlier (or crashed) run are gone and the schema always matches the DDL.
3. Resets data after every database test. Tests using `db_session` are rolled back. Tests whose rows are really committed (for example, through an API route) use the `clean_database` fixture, which empties every table afterwards.

By default the tests connect to:

```text
postgresql+psycopg2://localhost:5432/musicvault_test
```

The database credentials come from the `TEST_DATABASE_URL` environment variable. pytest does not read `.env`, so set it in your shell to use a different user, password, or port:

```bash
export TEST_DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/musicvault_test
python -m pytest
```

The database user needs permission to create databases (`CREATEDB`), or the test database must already exist and be owned by that user.

If no PostgreSQL server is reachable, the database tests are skipped and the rest still run.

GitHub Actions runs the same tests on every pull request and push to `master`, against a temporary PostgreSQL server that is discarded after each run. pytest creates the test database and schema there the same way it does locally. A failing test fails the workflow.

The tests never need real Spotify credentials or a network connection. Spotify's endpoints are faked, and configuration uses placeholder values.

| Test file | Covers |
|---|---|
| `test_spotify_oauth.py` | Login and callback: happy path, state/CSRF validation, Spotify-side failures |
| `test_protected_routes.py` | `login_required` on every protected route: unauthorized, tampered sessions, deleted users. Also `/me` and logout |
| `test_user_routes.py` | `/users/{id}`: own account allowed; other and nonexistent accounts forbidden |
| `test_config.py` | Secrets read from environment variables with no hardcoded fallbacks, and login returning `503` when any required variable is missing or empty |
| `test_database_framework.py` | The test database setup itself: schema built from the DDL, committed rows reset between tests, `db_session` rolled back, non-`_test` databases refused |

The same workflow also runs [gitleaks](https://github.com/gitleaks/gitleaks) over the branch's full history, and fails if a secret has been committed.

## Code Quality

### Frontend

Run oxlint:

```bash
npm run lint
```

Rules live in `frontend/.oxlintrc.json`. Warnings fail the run just like errors, and GitHub Actions runs this on every pull request.

### Backend

Check Python formatting:

```bash
black --check .
```

Run Ruff:

```bash
ruff check .
```

Automatically format Python code:

```bash
black .
```