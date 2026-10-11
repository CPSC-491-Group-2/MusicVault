from __future__ import annotations

import os

import pytest
from sqlalchemy import event
from sqlalchemy.engine import make_url
from sqlalchemy.exc import OperationalError

# Tests write real rows (e.g. test_user_routes commits a user), so they must
# never run against the dev database. They read TEST_DATABASE_URL instead of
# DATABASE_URL, and refuse to start unless the database name ends in "_test".
# This has to happen before db.session is imported, since it builds the engine.
TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL", "postgresql+psycopg2://localhost:5432/musicvault_test"
)
_test_db_name = make_url(TEST_DATABASE_URL).database or ""
if not _test_db_name.endswith("_test"):
    raise pytest.UsageError(
        "Refusing to run tests: TEST_DATABASE_URL must point at a database whose "
        f"name ends in '_test' (got {_test_db_name!r})."
    )
os.environ["DATABASE_URL"] = TEST_DATABASE_URL

from app import create_app  # noqa: E402
from db.session import SessionLocal, engine  # noqa: E402


@pytest.fixture
def client():
    app = create_app()
    app.testing = True
    return app.test_client()


@pytest.fixture
def require_live_database():
    """Skip the test cleanly if TEST_DATABASE_URL isn't reachable.

    CI sets REQUIRE_TEST_DATABASE so a missing database fails the job instead
    of silently skipping every account/database test.
    """
    try:
        connection = engine.connect()
    except OperationalError as exc:
        message = f"No live database reachable at TEST_DATABASE_URL: {exc}"
        if os.environ.get("REQUIRE_TEST_DATABASE"):
            pytest.fail(message)
        pytest.skip(message)
    else:
        connection.close()


@pytest.fixture
def db_session(require_live_database):
    """A Session bound to a SAVEPOINT that is rolled back after each test.

    Query functions call db.commit(); wrapping the connection in an outer
    transaction and restarting a SAVEPOINT after every commit keeps each
    test isolated without needing to touch the query functions themselves.
    """
    connection = engine.connect()
    outer_transaction = connection.begin()
    session = SessionLocal(bind=connection)
    session.begin_nested()

    @event.listens_for(session, "after_transaction_end")
    def _restart_savepoint(sess, trans):
        if trans.nested and not trans._parent.nested:
            sess.begin_nested()

    try:
        yield session
    finally:
        session.close()
        if connection.in_transaction():
            outer_transaction.rollback()
        connection.close()
