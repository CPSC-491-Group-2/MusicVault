from __future__ import annotations

import os

import pytest
from sqlalchemy import event
from sqlalchemy.exc import OperationalError

from app import create_app
from db.session import SessionLocal, engine


@pytest.fixture
def client():
    app = create_app()
    app.testing = True
    return app.test_client()


@pytest.fixture
def require_live_database():
    """Skip the test cleanly if DATABASE_URL isn't reachable.

    CI sets REQUIRE_TEST_DATABASE so a missing database fails the job instead
    of silently skipping every account/database test.
    """
    try:
        connection = engine.connect()
    except OperationalError as exc:
        message = f"No live database reachable at DATABASE_URL: {exc}"
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
