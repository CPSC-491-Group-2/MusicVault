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
