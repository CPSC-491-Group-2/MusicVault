from flask import g
from flask.views import MethodView
from flask_smorest import Blueprint

from app.auth import forbidden, login_required
from app.schemas.user import UserResponseSchema

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
    # Runs before flask-smorest's response handling, so a 401 short-circuits
    # without touching the view.
    decorators = [login_required]

    @user_bp.response(200, UserResponseSchema)
    @user_bp.alt_response(401, description="Not logged in")
    def get(self):
        return g.current_user
