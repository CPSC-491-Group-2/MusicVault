# MusicVault

MusicVault is a web application for discovering, searching, saving,
and organizing music.

This repository contains the MusicVault frontend and backend applications.

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

## Repository Structure

```text
musicvault/
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
├── .gitignore
└── README.md

## API Contract

MusicVault uses a REST API provided by the Flask backend.

API endpoints are versioned under:

```text
/api/v1
```

For example:

```text
GET /api/v1/health
```

Successful API responses use JSON.

Example:

```json
{
  "service": "MusicVault API",
  "status": "ok"
}
```

The frontend maintains TypeScript interfaces for expected API
responses in:

```text
frontend/types/api.ts
```

Backend and frontend changes to an API response should be updated
together to keep the API contract synchronized.

### Error Format

API errors use the following structure:

```json
{
  "error": "Not Found",
  "message": "The requested resource was not found."
}
```

## OpenAPI Documentation

The Flask backend exposes interactive OpenAPI documentation.

Start the backend:

```bash
cd backend
python run.py
```

Swagger UI is available at:

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