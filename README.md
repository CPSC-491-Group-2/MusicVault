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

## Planned Technology Stack

The current planned stack includes:

- **Frontend:** Next.js
- **Backend:** Flask
- **Database:** PostgreSQL
- **Database ORM:** SQLAlchemy
- **External API:** Spotify Web API
- **Version Control:** GitHub
- **Project Management:** Jira

The architecture and individual technologies may be adjusted as the team evaluates the existing MusicVault prototype and completes Sprint 1.

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

1. Pull the latest version of the main branch.
2. Create a branch for the assigned Jira task.
3. Make and test changes on that branch.
4. Commit and push the branch to GitHub.
5. Open a Pull Request.
6. Have another team member review the Pull Request.
7. Merge approved changes into the main branch.

Code should not be pushed directly to the main branch.

## Project Structure

The project structure is currently being established during Sprint 1.

Planned structure:

```text
MusicVault/
├── frontend/        # Next.js frontend
├── backend/         # Flask backend/API
├── database/        # Database configuration/models
├── docs/            # Project documentation
└── README.md

* subject to change *
