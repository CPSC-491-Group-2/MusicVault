"""
SOC 2 Data Classification Control (C-1)

Every database column must have a classification, and the SQLAlchemy model
labels, the inventory CSV and the schema built from the DDL must all agree.
The handling tests at the end check that Confidential and Restricted values
stay out of __repr__, API responses and plaintext storage.
See docs/data-classification.md.
"""

from __future__ import annotations

import inspect

import pytest
from marshmallow import Schema
from sqlalchemy import Column, Integer, MetaData, String, Table, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

import app.schemas.auth
import app.schemas.health
import app.schemas.spotify
import app.schemas.user
from db.session import SessionLocal, engine
from models import Base, SpotifyAccount, User
from models.classification import (
    DataClass,
    classification_problems,
    classified,
    column_classifications,
    load_inventory,
)

pytestmark = pytest.mark.data_classification


def test_every_model_column_is_classified():
    assert classification_problems(Base.metadata) == []


def test_model_labels_match_inventory():
    inventory = load_inventory()
    mismatches = {
        name: {"model": label, "inventory": inventory.get(name)}
        for name, label in column_classifications(Base.metadata).items()
        if name not in inventory or inventory[name] != label
    }
    assert mismatches == {}


# Fields whose level the policy fixes. Matching the inventory isn't enough on
# its own: a token downgraded in both the model and the CSV would still match.
KNOWN_SENSITIVE_FIELDS = {
    "users.password_hash": DataClass.RESTRICTED,
    "spotify_accounts.access_token": DataClass.RESTRICTED,
    "spotify_accounts.refresh_token": DataClass.RESTRICTED,
    "users.id": DataClass.CONFIDENTIAL,
    "users.email": DataClass.CONFIDENTIAL,
    "users.display_name": DataClass.CONFIDENTIAL,
    "spotify_accounts.user_id": DataClass.CONFIDENTIAL,
    "spotify_accounts.spotify_account_id": DataClass.CONFIDENTIAL,
    "spotify_accounts.spotify_user_id": DataClass.CONFIDENTIAL,
    "spotify_accounts.display_name": DataClass.CONFIDENTIAL,
    "spotify_accounts.email": DataClass.CONFIDENTIAL,
    "user_preferences.user_id": DataClass.CONFIDENTIAL,
    "user_preferences.preference_type": DataClass.CONFIDENTIAL,
    "user_preferences.rating": DataClass.CONFIDENTIAL,
    "user_top_songs.user_id": DataClass.CONFIDENTIAL,
    "user_top_songs.rank": DataClass.CONFIDENTIAL,
    "recommendations.user_id": DataClass.CONFIDENTIAL,
    "recommendations.score": DataClass.CONFIDENTIAL,
    "recommendations.reason": DataClass.CONFIDENTIAL,
}


def test_known_sensitive_fields_are_classified_correctly():
    inventory = load_inventory()
    models = column_classifications(Base.metadata)
    wrong = {
        name: {
            "required": required,
            "inventory": inventory.get(name),
            "model": models.get(name),
        }
        for name, required in KNOWN_SENSITIVE_FIELDS.items()
        if inventory.get(name) != required or models.get(name, required) != required
    }
    assert wrong == {}


def test_inventory_uses_only_defined_levels():
    valid = {level.value for level in DataClass}
    invalid = {
        name: label for name, label in load_inventory().items() if label not in valid
    }
    assert invalid == {}


def test_inventory_matches_live_schema(require_live_database):
    """Covers tables without a model too, e.g. recommendations and charts."""
    with engine.connect() as connection:
        schema = {
            f"{table}.{column}"
            for table, column in connection.execute(
                text(
                    "SELECT table_name, column_name FROM information_schema.columns "
                    "WHERE table_schema = 'public'"
                )
            )
        }
    inventory = set(load_inventory())

    assert sorted(schema - inventory) == [], "columns missing from the inventory"
    assert sorted(inventory - schema) == [], "inventory lists columns that don't exist"


# The checks above only prove something if the validator really catches a
# missing label, so check that against a model built to fail.


def test_unclassified_model_column_is_reported():
    class ScratchBase(DeclarativeBase):
        pass

    class Scratch(ScratchBase):
        __tablename__ = "scratch"

        id: Mapped[int] = mapped_column(
            primary_key=True, info=classified(DataClass.INTERNAL)
        )
        nickname: Mapped[str] = mapped_column(String(50))

    assert classification_problems(ScratchBase.metadata) == [
        "scratch.nickname: no classification"
    ]


def test_unknown_classification_is_reported():
    metadata = MetaData()
    Table("scratch", metadata, Column("id", Integer, info={"classification": "secret"}))

    assert classification_problems(metadata) == [
        "scratch.id: unknown classification 'secret'"
    ]


def test_duplicate_inventory_row_is_rejected(tmp_path):
    inventory = tmp_path / "inventory.csv"
    inventory.write_text(
        "table,column,classification,category,rationale\n"
        "users,email,confidential,Contact PII,x\n"
        "users,email,public,Contact PII,x\n"
    )

    with pytest.raises(ValueError, match="users.email more than once"):
        load_inventory(inventory)


# ============================================================
# HANDLING REQUIREMENTS (policy section 3)
# ============================================================

SENSITIVE = {DataClass.CONFIDENTIAL, DataClass.RESTRICTED}
RESTRICTED_COLUMNS = {
    name.split(".")[1]
    for name, label in load_inventory().items()
    if label == DataClass.RESTRICTED
}


def _sentinel(column, number):
    """A value unlikely to appear in a repr by chance, of the column's type."""
    python_type = column.type.python_type
    if python_type is str:
        return f"SENTINEL{number}"
    if python_type is int:
        return 900000 + number
    raise TypeError(f"no sentinel for {column} ({python_type})")


@pytest.mark.parametrize(
    "model",
    [mapper.class_ for mapper in Base.registry.mappers],
    ids=lambda model: model.__name__,
)
def test_model_repr_hides_sensitive_values(model):
    """Logs and tracebacks print reprs, so they may show only keys and Public
    or Internal values. Keys identify a row and are allowed for debugging."""
    instance = model()
    values = {}
    for number, column in enumerate(model.__table__.columns):
        if column.primary_key or column.foreign_keys:
            continue
        if column.info.get("classification") in SENSITIVE:
            values[column.name] = _sentinel(column, number)
            setattr(instance, column.name, values[column.name])

    shown = {
        name: value for name, value in values.items() if str(value) in repr(instance)
    }
    assert shown == {}


def test_response_schemas_have_no_restricted_fields():
    schemas = [
        schema
        for module in (
            app.schemas.auth,
            app.schemas.health,
            app.schemas.spotify,
            app.schemas.user,
        )
        for _, schema in inspect.getmembers(module, inspect.isclass)
        if issubclass(schema, Schema) and schema.__name__.endswith("ResponseSchema")
    ]
    assert schemas, "no response schemas found"

    exposed = {
        schema.__name__: sorted(RESTRICTED_COLUMNS & set(schema().fields))
        for schema in schemas
        if RESTRICTED_COLUMNS & set(schema().fields)
    }
    assert exposed == {}


def test_user_responses_never_include_restricted_values(auth_client, log_in, db_user):
    with SessionLocal() as db:
        user = db.get(User, db_user)
        user.password_hash = "SENTINEL-password-hash"
        db.add(
            SpotifyAccount(
                user_id=db_user,
                spotify_account_id="sentinel-account",
                access_token="SENTINEL-access-token",
                refresh_token="SENTINEL-refresh-token",
            )
        )
        db.commit()
    log_in(db_user)

    for path in (f"/api/v1/users/{db_user}", "/api/v1/me"):
        response = auth_client.get(path)
        assert response.status_code == 200
        assert "SENTINEL" not in response.get_data(as_text=True), path


def test_database_errors_hide_bound_values(require_live_database):
    """Routes log failed token saves with logger.exception, and SQLAlchemy
    adds the statement's bound values to the error text unless the engine
    sets hide_parameters. Division by zero is used because Postgres doesn't
    echo the statement back for it, so only SQLAlchemy's copy is tested.

    Postgres itself can still echo values (psycopg2 binds them client side),
    e.g. "LINE 1: ... 'token'" for type errors; see the assessment."""
    with pytest.raises(DBAPIError) as caught, engine.connect() as connection:
        connection.execute(
            text("SELECT CAST(:token AS text), 1 / 0"),
            {"token": "SENTINEL-access-token"},
        )

    assert "SENTINEL" not in str(caught.value)


@pytest.mark.xfail(
    strict=True,
    reason="Spotify tokens are stored in plaintext; application-level encryption "
    "is tracked as remediation work (see the Sprint 4 assessment)",
)
def test_spotify_tokens_are_not_stored_in_plaintext(clean_database, make_db_user):
    """Policy section 3: Restricted values are hashed or encrypted at the
    application level. When encryption lands this starts passing, and strict
    xfail turns that into a failure so the marker gets removed."""
    with SessionLocal() as db:
        db.add(
            SpotifyAccount(
                user_id=make_db_user(),
                spotify_account_id="sentinel-account",
                access_token="SENTINEL-access-token",
                refresh_token="SENTINEL-refresh-token",
            )
        )
        db.commit()

    with engine.connect() as connection:
        stored = connection.execute(
            text("SELECT access_token, refresh_token FROM spotify_accounts")
        ).one()

    assert stored.access_token != "SENTINEL-access-token"
    assert stored.refresh_token != "SENTINEL-refresh-token"
