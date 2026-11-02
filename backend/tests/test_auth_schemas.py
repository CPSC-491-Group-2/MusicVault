import pytest
from marshmallow import ValidationError

from app.schemas.auth import (
    LoginRequestSchema,
    RegisterRequestSchema,
)


def test_register_schema_accepts_valid_data():
    schema = RegisterRequestSchema()

    result = schema.load({
        "email": "test@example.com",
        "password": "ExamplePassword123",
        "display_name": "Test User",
    })

    assert result["email"] == "test@example.com"
    assert result["display_name"] == "Test User"


def test_register_schema_rejects_invalid_email():
    schema = RegisterRequestSchema()

    with pytest.raises(ValidationError):
        schema.load({
            "email": "invalid-email",
            "password": "ExamplePassword123",
        })


def test_login_schema_requires_password():
    schema = LoginRequestSchema()

    with pytest.raises(ValidationError):
        schema.load({
            "email": "test@example.com",
        })