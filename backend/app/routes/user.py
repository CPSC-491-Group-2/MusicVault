from flask import g
from flask.views import MethodView
from flask_smorest import Blueprint
from sqlalchemy import select

from app.auth import forbidden, login_required
from app.schemas.user import CurrentUserResponseSchema, UserResponseSchema
from db.session import SessionLocal
from models.spotify_account import SpotifyAccount

user_bp = Blueprint(
    "users",
    __name__,
    description="User account endpoints",
)


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
        user = g.current_user

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
