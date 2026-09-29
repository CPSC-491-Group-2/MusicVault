from __future__ import annotations

import pytest
from sqlalchemy import event
from sqlalchemy.exc import OperationalError

from db.session import SessionLocal, engine


@pytest.fixture
def db_session():
    """A Session bound to a SAVEPOINT that is rolled back after each test.

    Query functions call db.commit(); wrapping the connection in an outer
    transaction and restarting a SAVEPOINT after every commit keeps each
    test isolated without needing to touch the query functions themselves.
    """
    try:
        connection = engine.connect()
    except OperationalError as exc:
        pytest.skip(f"No live database reachable at DATABASE_URL: {exc}")
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
