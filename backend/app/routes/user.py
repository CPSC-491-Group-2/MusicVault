from flask import g
from flask.views import MethodView
from flask_smorest import Blueprint, abort

from app.auth import login_required
from app.schemas.user import UserResponseSchema
from db.queries.user import get_user_by_id
from db.session import SessionLocal

user_bp = Blueprint(
    "users",
    __name__,
    description="User account endpoints",
)


@user_bp.route("/users/<uuid:user_id>")
class UserResource(MethodView):

    @user_bp.response(200, UserResponseSchema)
    def get(self, user_id):
        with SessionLocal() as db:
            user = get_user_by_id(db, user_id)

        if user is None:
            abort(404, message="User not found")

        return user


@user_bp.route("/me")
class CurrentUserResource(MethodView):
    # Runs before flask-smorest's response handling, so a 401 short-circuits
    # without touching the view.
    decorators = [login_required]

    @user_bp.response(200, UserResponseSchema)
    @user_bp.alt_response(401, description="Not logged in")
    def get(self):
        return g.current_user
