"""Tests for the test-database setup in conftest.py itself."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from sqlalchemy import func, select, text

from db.queries.user import create_user
from db.session import SessionLocal
from models.user import User

BACKEND_DIR = Path(__file__).resolve().parent.parent

SCHEMA_TABLES = {
    "users",
    "spotify_accounts",
    "songs",
    "user_preferences",
    "recommendations",
    "charts",
    "chart_entries",
    "user_top_songs",
}


def test_schema_is_built_from_ddl(require_live_database):
    with SessionLocal() as db:
        tables = set(
            db.scalars(
                text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")
            )
        )
    assert tables == SCHEMA_TABLES


# These two run in file order: the first commits a row for real, and the
# second checks clean_database removed it before the next test.


def test_clean_database_commits_a_row(clean_database):
    with SessionLocal() as db:
        create_user(db, email="framework-leftover@example.com")
        assert db.scalar(select(func.count()).select_from(User)) == 1


def test_clean_database_leaves_no_rows_behind(require_live_database):
    with SessionLocal() as db:
        assert db.scalar(select(func.count()).select_from(User)) == 0


def test_db_session_changes_are_rolled_back(db_session):
    create_user(db_session, email="rolled-back@example.com")

    with SessionLocal() as other:
        assert other.scalar(select(func.count()).select_from(User)) == 0


def test_refuses_a_database_not_ending_in_test():
    env = {
        **os.environ,
        "TEST_DATABASE_URL": "postgresql+psycopg2://localhost:5432/musicvault",
    }
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "--collect-only",
            "-q",
            "tests/test_health.py",
        ],
        cwd=BACKEND_DIR,
        env=env,
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "Refusing to run tests" in result.stdout + result.stderr
