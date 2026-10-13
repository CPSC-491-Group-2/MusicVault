"""Spotify API endpoints for authenticated MusicVault users."""

import uuid
from datetime import datetime, timedelta, timezone

from flask import current_app, jsonify, make_response, session
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select

from app.schemas.spotify import (
    SpotifyTopTracksQuerySchema,
    SpotifyTopTracksResponseSchema,
)
from app.services.spotify_auth import (
    SpotifyAuthError,
    SpotifyRefreshTokenError,
    refresh_access_token,
)
from db.queries.user import get_user_by_id
from db.session import SessionLocal
from models.spotify_account import SpotifyAccount
from services.spotify_service import (
    SpotifyAuthenticationError,
    SpotifyPermissionError,
    SpotifyRateLimitError,
    SpotifyResourceNotFoundError,
    SpotifyService,
    SpotifyServiceError,
)

spotify_bp = Blueprint(
    "spotify",
    __name__,
    description="Spotify listening data endpoints",
)


def _refresh_rejected_token(user_uuid, rejected_token):
    """Refresh a rejected Spotify token and persist the replacement."""

    with SessionLocal() as db:
        try:
            account = db.scalar(
                select(SpotifyAccount)
                .where(SpotifyAccount.user_id == user_uuid)
                .with_for_update()
            )
        except SQLAlchemyError:
            db.rollback()
            current_app.logger.exception(
                "Failed to lock Spotify account for token refresh"
            )
            abort(
                503,
                message="MusicVault database temporarily unavailable",
            )

        if account is None:
            # Check whether the user still exists to distinguish
            # an invalid session from an unlinked Spotify account.
            try:
                user = get_user_by_id(db, user_uuid)
            except SQLAlchemyError:
                db.rollback()
                current_app.logger.exception(
                    "Failed to retrieve user during Spotify token refresh"
                )
                abort(
                    503,
                    message="MusicVault database temporarily unavailable",
                )

            if user is None:
                abort(401, message="User session is no longer valid")

            abort(403, message="Spotify account not linked")

        # Another request may already have refreshed this token.
        # Reuse its replacement rather than refreshing again.
        if account.access_token and account.access_token != rejected_token:
            return account.access_token

        if not account.refresh_token:
            abort(401, message="Spotify reconnection required")

        client_id = current_app.config.get("SPOTIFY_CLIENT_ID")
        client_secret = current_app.config.get("SPOTIFY_CLIENT_SECRET")

        if not client_id or not client_secret:
            abort(503, message="Spotify service is not configured")

        try:
            token_data = refresh_access_token(
                refresh_token=account.refresh_token,
                client_id=client_id,
                client_secret=client_secret,
            )

        except SpotifyRefreshTokenError:
            current_app.logger.warning(
                "Spotify refresh token rejected for user %s",
                user_uuid,
            )
            abort(401, message="Spotify reconnection required")

        except SpotifyAuthError:
            current_app.logger.warning(
                "Spotify refresh service unavailable for user %s",
                user_uuid,
            )
            abort(
                502,
                message="Spotify authentication service unavailable",
            )

        account.access_token = token_data["access_token"]

        # Spotify may not return a new refresh token.
        account.refresh_token = token_data.get("refresh_token") or account.refresh_token

        account.token_expires_at = datetime.now(timezone.utc) + timedelta(
            seconds=int(token_data.get("expires_in", 3600))
        )

        if token_data.get("scope") is not None:
            account.scope = token_data["scope"]

        try:
            db.commit()
        except SQLAlchemyError:
            db.rollback()
            current_app.logger.exception("Failed to save refreshed Spotify credentials")
            abort(
                503,
                message="MusicVault database temporarily unavailable",
            )

        return account.access_token


@spotify_bp.route("/spotify/top-tracks")
class SpotifyTopTracksResource(MethodView):

    @spotify_bp.arguments(
        SpotifyTopTracksQuerySchema,
        location="query",
    )
    @spotify_bp.response(200, SpotifyTopTracksResponseSchema)
    def get(self, args):
        """Return the current user's normalized top Spotify tracks."""

        # Identify the authenticated MusicVault user.
        user_id = session.get("user_id")

        if not user_id:
            abort(401, message="Authentication required")

        try:
            user_uuid = uuid.UUID(str(user_id))
        except (ValueError, TypeError):
            abort(401, message="Invalid authentication session")

        # Retrieve and lock the user's linked Spotify account.
        with SessionLocal() as db:
            try:
                spotify_account = db.scalar(
                    select(SpotifyAccount)
                    .where(SpotifyAccount.user_id == user_uuid)
                    .with_for_update()
                )
            except SQLAlchemyError:
                db.rollback()
                current_app.logger.exception("Failed to retrieve Spotify account")
                abort(
                    503,
                    message="MusicVault database temporarily unavailable",
                )

            if spotify_account is None:
                try:
                    user = get_user_by_id(db, user_uuid)
                except SQLAlchemyError:
                    db.rollback()
                    current_app.logger.exception("Failed to retrieve user")
                    abort(
                        503,
                        message="MusicVault database temporarily unavailable",
                    )

                if user is None:
                    abort(401, message="User session is no longer valid")

                abort(403, message="Spotify account not linked")

            access_token = spotify_account.access_token
            expires_at = spotify_account.token_expires_at

            # Refresh tokens that have expired or will expire soon.
            now = datetime.now(timezone.utc)
            needs_refresh = not access_token or not expires_at

            if expires_at is not None:
                if expires_at.tzinfo is None:
                    expires_at = expires_at.replace(tzinfo=timezone.utc)

                needs_refresh = needs_refresh or expires_at <= now + timedelta(
                    seconds=60
                )

            if needs_refresh:
                if not spotify_account.refresh_token:
                    abort(401, message="Spotify reconnection required")

                client_id = current_app.config.get("SPOTIFY_CLIENT_ID")
                client_secret = current_app.config.get("SPOTIFY_CLIENT_SECRET")

                if not client_id or not client_secret:
                    abort(
                        503,
                        message="Spotify service is not configured",
                    )

                try:
                    token_data = refresh_access_token(
                        refresh_token=spotify_account.refresh_token,
                        client_id=client_id,
                        client_secret=client_secret,
                    )

                except SpotifyRefreshTokenError:
                    current_app.logger.warning(
                        "Spotify refresh token rejected for user %s",
                        user_uuid,
                    )
                    abort(
                        401,
                        message="Spotify reconnection required",
                    )

                except SpotifyAuthError:
                    current_app.logger.warning(
                        "Spotify refresh service unavailable for user %s",
                        user_uuid,
                    )
                    abort(
                        502,
                        message="Spotify authentication service unavailable",
                    )

                access_token = token_data["access_token"]

                spotify_account.access_token = access_token
                spotify_account.refresh_token = (
                    token_data.get("refresh_token") or spotify_account.refresh_token
                )
                spotify_account.token_expires_at = datetime.now(
                    timezone.utc
                ) + timedelta(seconds=int(token_data.get("expires_in", 3600)))

                if token_data.get("scope") is not None:
                    spotify_account.scope = token_data["scope"]

                try:
                    db.commit()
                except SQLAlchemyError:
                    db.rollback()
                    current_app.logger.exception(
                        "Failed to save refreshed Spotify credentials"
                    )
                    abort(
                        503,
                        message="MusicVault database temporarily unavailable",
                    )

        # Fetch tracks after the database session closes.
        try:
            for attempt in range(2):
                spotify_service = SpotifyService(access_token)

                try:
                    tracks = spotify_service.get_normalized_user_top_tracks(
                        limit=args["limit"],
                        time_range=args["time_range"],
                        offset=args["offset"],
                    )
                    return tracks

                except SpotifyAuthenticationError:
                    if attempt == 1:
                        abort(
                            401,
                            message="Spotify reconnection required",
                        )

                    # Refresh once, then retry with the new token.
                    access_token = _refresh_rejected_token(
                        user_uuid,
                        access_token,
                    )

        except SpotifyPermissionError:
            abort(403, message="Spotify permission denied")

        except SpotifyRateLimitError as exc:
            retry_after = exc.retry_after

            if isinstance(retry_after, str) and retry_after.isdecimal():
                retry_after = str(min(int(retry_after), 86400))
            else:
                retry_after = None

            response = {
                "error": "Too Many Requests",
                "message": "Spotify rate limit exceeded",
            }

            result = make_response(jsonify(response), 429)

            if retry_after is not None:
                result.headers["Retry-After"] = retry_after

            return result

        except SpotifyResourceNotFoundError:
            abort(502, message="Spotify resource unavailable")

        except SpotifyServiceError:
            abort(502, message="Spotify service unavailable")

        except ValueError:
            abort(502, message="Invalid response from Spotify")
