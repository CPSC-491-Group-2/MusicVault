from flask.views import MethodView
from flask_smorest import Blueprint, abort

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
