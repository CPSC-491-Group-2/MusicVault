from flask import jsonify
from flask_smorest import Blueprint

from app.auth import logout_user
from app.schemas.auth import LoginRequestSchema, RegisterRequestSchema


account_bp = Blueprint(
    "account",
    __name__,
    description="MusicVault local account authentication",
)


@account_bp.post("/auth/register")
@account_bp.arguments(RegisterRequestSchema)
def register(data):
    """Register a new MusicVault account."""

    # Pending integration of password hashing/security module.
    return jsonify({
        "error": "Service Unavailable",
        "message": "Local registration is not enabled yet.",
    }), 503


@account_bp.post("/auth/login")
@account_bp.arguments(LoginRequestSchema)
def login(data):
    """Authenticate an existing MusicVault account."""

    # Pending integration of password verification/security module.
    return jsonify({
        "error": "Service Unavailable",
        "message": "Local login is not enabled yet.",
    }), 503


@account_bp.post("/auth/logout")
def logout():
    """End the current MusicVault session."""

    logout_user()
    return "", 204