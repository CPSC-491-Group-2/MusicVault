from flask import g
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import IntegrityError

from app.auth import (
    error_response,
    login_required,
    login_user,
    logout_user,
    session_revoked,
)
from app.routes.user import current_user_payload
from app.schemas.auth import (
    EmailSchema,
    LoginRequestSchema,
    PasswordChangeSchema,
    RegisterRequestSchema,
)
from app.schemas.user import CurrentUserResponseSchema
from app.security.passwords import (
    hash_password,
    needs_rehash,
    verify_dummy,
    verify_password,
)
from db.queries.spotify_account import unlink_spotify
from db.queries.user import (
    create_user,
    get_user_by_email,
    get_user_by_id,
    rehash_password,
    set_password,
)
from db.session import SessionLocal


account_bp = Blueprint(
    "account",
    __name__,
    description="MusicVault local account authentication",
)


def _email_taken():
    return error_response(
        409, "email_taken", "An account with this email already exists."
    )


def _invalid_credentials():
    return error_response(401, "invalid_credentials", "Incorrect email or password.")


@account_bp.post("/auth/register")
@account_bp.arguments(RegisterRequestSchema)
@account_bp.response(201, CurrentUserResponseSchema)
@account_bp.alt_response(409, description="Email already registered")
def register(data):
    """Register a new MusicVault account."""

    password_hash = hash_password(data["password"])

    with SessionLocal() as db:
        try:
            user = create_user(
                db,
                email=data["email"],
                display_name=data["display_name"],
                password_hash=password_hash,
            )
        except IntegrityError:
            return _email_taken()

    login_user(user.id, user.auth_version)
    return current_user_payload(user)


@account_bp.post("/auth/login")
@account_bp.arguments(LoginRequestSchema)
@account_bp.response(200, CurrentUserResponseSchema)
@account_bp.alt_response(401, description="Incorrect email or password")
def login(data):
    """Authenticate an existing MusicVault account."""

    password = data["password"]

    with SessionLocal() as db:
        user = get_user_by_email(db, data["email"])

        if user is None or not user.password_hash:
            # Same work as a real verify, so timing can't reveal which emails exist.
            verify_dummy(password)
            return _invalid_credentials()

        if not verify_password(user.password_hash, password):
            return _invalid_credentials()

        # The session gets the version this password was checked against.
        user_id, auth_version = user.id, user.auth_version

        if needs_rehash(user.password_hash) and not rehash_password(
            db, user, hash_password(password)
        ):
            return _invalid_credentials()

        payload = current_user_payload(user)

    login_user(user_id, auth_version)
    return payload


@account_bp.post("/auth/logout")
def logout():
    """End the current MusicVault session."""

    logout_user()
    return "", 204


@account_bp.route("/me/password")
class PasswordResource(MethodView):
    decorators = [login_required]

    @account_bp.arguments(PasswordChangeSchema)
    @account_bp.response(200, CurrentUserResponseSchema)
    @account_bp.alt_response(401, description="Not logged in")
    @account_bp.alt_response(403, description="Current password is incorrect")
    @account_bp.alt_response(409, description="Email already registered")
    def put(self, data):
        user = g.current_user
        email = None

        if user.password_hash:
            current_password = data["current_password"]
            if not current_password or not verify_password(
                user.password_hash, current_password
            ):
                return error_response(
                    403, "current_password_wrong", "The current password is incorrect."
                )
        elif user.email is None:
            # A Spotify-only account without an email needs one to log in with.
            given = {} if data["email"] is None else {"email": data["email"]}
            errors = EmailSchema().validate(given)
            if errors:
                abort(422, errors={"json": errors})
            email = data["email"]

        new_hash = hash_password(data["new_password"])

        with SessionLocal() as db:
            try:
                auth_version = set_password(
                    db,
                    user.id,
                    new_hash,
                    expected_version=user.auth_version,
                    email=email,
                )
            except IntegrityError:
                return _email_taken()

            if auth_version is None:
                logout_user()
                return session_revoked()

            payload = current_user_payload(get_user_by_id(db, user.id))

        login_user(user.id, auth_version)
        return payload


@account_bp.route("/me/spotify")
class SpotifyConnectionResource(MethodView):
    decorators = [login_required]

    @account_bp.response(200, CurrentUserResponseSchema)
    @account_bp.alt_response(401, description="Not logged in")
    @account_bp.alt_response(409, description="Account has no password")
    def delete(self):
        user = g.current_user

        if not user.password_hash:
            return error_response(
                409, "password_required", "Set a password before disconnecting Spotify."
            )

        with SessionLocal() as db:
            unlink_spotify(db, user.id)

        return current_user_payload(user)
