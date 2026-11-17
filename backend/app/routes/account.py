
from flask import current_app, jsonify
from flask_smorest import Blueprint
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from werkzeug.security import generate_password_hash, check_password_hash

from app.auth import login_user, logout_user
from app.schemas.auth import LoginRequestSchema, RegisterRequestSchema
from db.queries.user import (
    create_user,
    get_user_by_email,
    normalize_email,
)
from db.session import SessionLocal


account_bp = Blueprint(
    "account",
    __name__,
    description="MusicVault local account authentication",
)


@account_bp.post("/auth/register")
@account_bp.arguments(RegisterRequestSchema)
def register(data):
    """Register a new MusicVault account."""

    email = normalize_email(data["email"])
    password = data["password"]
    display_name = data.get("display_name")

    with SessionLocal() as db:
        try:
            existing_user = get_user_by_email(db, email)

            if existing_user is not None:
                return jsonify({
                    "error": "Conflict",
                    "message": "An account with this email already exists.",
                }), 409

            password_hash = generate_password_hash(
                password,
                method="scrypt",
            )

            user = create_user(
                db,
                email=email,
                display_name=display_name,
                password_hash=password_hash,
            )

            user_id = user.id
            user_email = user.email
            user_display_name = user.display_name

        except IntegrityError:
            db.rollback()
            return jsonify({
                "error": "Conflict",
                "message": "An account with this email already exists.",
            }), 409

        except SQLAlchemyError:
            db.rollback()

            current_app.logger.exception(
                "Database error during local account registration"
             )
            return jsonify({
                "error": "Internal Server Error",
                "message": "Unable to create account.",
            }), 500

    login_user(user_id)

    return jsonify({
        "id": str(user_id),
        "email": user_email,
        "display_name": user_display_name,
    }), 201


@account_bp.post("/auth/login")
@account_bp.arguments(LoginRequestSchema)
def login(data):
    """Authenticate an existing MusicVault account."""

    email = normalize_email(data["email"])
    password = data["password"]

    with SessionLocal() as db:
        try:
            user = get_user_by_email(db, email)

            if (
                user is None
                or user.password_hash is None
                or not check_password_hash(user.password_hash, password)
            ):
                return jsonify({
                    "error": "Unauthorized",
                    "message": "Invalid email or password.",
                }), 401

            user_id = user.id
            user_email = user.email
            user_display_name = user.display_name

        except SQLAlchemyError:
            return jsonify({
                "error": "Internal Server Error",
                "message": "Unable to authenticate.",
            }), 500

    login_user(user_id)

    return jsonify({
        "id": str(user_id),
        "email": user_email,
        "display_name": user_display_name,
    }), 200


@account_bp.post("/auth/logout")
def logout():
    """End the current MusicVault session."""

    logout_user()
    return "", 204
