from flask import current_app, g
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from app.auth import error_response, forbidden, login_required, logout_user
from app.schemas.auth import DeleteAccountSchema
from app.schemas.user import CurrentUserResponseSchema, UserResponseSchema
from app.security.passwords import verify_password
from db.queries.user import delete_user
from db.session import SessionLocal
from models.spotify_account import SpotifyAccount

DELETE_CONFIRM_PHRASE = "delete my account"

user_bp = Blueprint(
    "users",
    __name__,
    description="User account endpoints",
)


def current_user_payload(user) -> dict:
    # Query Spotify information in an active database session.
    with SessionLocal() as db:
        spotify_account = db.scalar(
            select(SpotifyAccount).where(
                SpotifyAccount.user_id == user.id
            )
        )

        spotify_info = {
            "connected": spotify_account is not None,
            "display_name": (
                spotify_account.display_name
                if spotify_account is not None
                else None
            ),
        }

    return {
        "id": user.id,
        "email": user.email,
        "display_name": user.display_name,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
        "has_password": bool(user.password_hash),
        "spotify": spotify_info,
    }


@user_bp.route("/users/<uuid:user_id>")
class UserResource(MethodView):
    decorators = [login_required]

    @user_bp.response(200, UserResponseSchema)
    @user_bp.alt_response(401, description="Not logged in")
    @user_bp.alt_response(403, description="Not the logged-in user's account")
    def get(self, user_id):
        # Users can only read their own account. Any other ID gets 403, even
        # one that doesn't exist, so this can't be used to probe for accounts.
        if user_id != g.current_user.id:
            return forbidden()

        return g.current_user


@user_bp.route("/me")
class CurrentUserResource(MethodView):
    decorators = [login_required]

    @user_bp.response(200, CurrentUserResponseSchema)
    @user_bp.alt_response(401, description="Not logged in")
    def get(self):
        return current_user_payload(g.current_user)

    @user_bp.arguments(DeleteAccountSchema)
    @user_bp.response(204)
    @user_bp.alt_response(401, description="Not logged in")
    @user_bp.alt_response(403, description="Current password is incorrect")
    @user_bp.alt_response(422, description="Confirmation phrase missing or wrong")
    def delete(self, data):
        user = g.current_user

        confirm = (data["confirm"] or "").strip().lower()
        if confirm != DELETE_CONFIRM_PHRASE:
            abort(
                422,
                errors={"json": {"confirm": ['Type "delete my account" to confirm.']}},
            )

        if user.password_hash:
            password = data["password"]
            if not password or not verify_password(user.password_hash, password):
                return error_response(
                    403, "current_password_wrong", "The current password is incorrect."
                )

        with SessionLocal() as db:
            try:
                delete_user(db, user.id)
            except SQLAlchemyError:
                db.rollback()
                current_app.logger.exception("Failed to delete account")
                abort(
                    503,
                    message="MusicVault database temporarily unavailable",
                )

        current_app.logger.warning("Deleted account %s", user.id)
        logout_user()
        return "", 204
