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
- ESLint

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

## Code Quality

### Frontend

Run ESLint:

```bash
npm run lint
```

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