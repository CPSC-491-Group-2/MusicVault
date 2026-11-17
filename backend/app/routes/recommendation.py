"""Recommendation API endpoints."""

from flask import current_app, g
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError

from app.auth import login_required
from app.schemas.recommendation import RecommendationResponseSchema
from app.services.similarity import rank_candidates, track_features_from_song
from db.queries.recommendations import get_recommendation_inputs
from db.session import SessionLocal


recommendation_bp = Blueprint(
    "recommendations",
    __name__,
    description="Personalized music recommendation endpoints",
)


@recommendation_bp.route("/recommendations")
class RecommendationResource(MethodView):
    decorators = [login_required]

    @recommendation_bp.response(200, RecommendationResponseSchema)
    @recommendation_bp.alt_response(401, description="Not logged in")
    @recommendation_bp.alt_response(
        503,
        description="MusicVault database temporarily unavailable",
    )
    def get(self):
        """Return ranked recommendations for the current user."""

        with SessionLocal() as db:
            try:
                inputs = get_recommendation_inputs(
                    db,
                    g.current_user.id,
                    time_range="medium_term",
                )

                if not inputs.seeds:
                    return {
                        "items": [],
                        "total": 0,
                    }

                seed_features = [
                    track_features_from_song(song)
                    for song in inputs.seeds
                ]

                candidate_features = [
                    track_features_from_song(song)
                    for song in inputs.candidates
                ]

                ranked = rank_candidates(
                    seed_features,
                    candidate_features,
                    limit=20,
                )

                songs_by_id = {
                    str(song.id): song
                    for song in inputs.candidates
                }

                items = []

                for recommendation in ranked:
                    song = songs_by_id.get(
                        recommendation.track_id
                    )

                    if song is None:
                        continue

                    items.append(
                        {
                            "id": song.id,
                            "title": song.title,
                            "artist": song.artist_name,
                            "album": song.album_name,
                            "spotify_track_id": song.spotify_track_id,
                            "spotify_url": song.spotify_url,
                            "album_image_url": song.album_image_url,
                            "popularity": song.popularity,
                            "score": recommendation.score,
                            "reason": recommendation.reason,
                            "components": recommendation.components,
                        }
                    )

            except SQLAlchemyError:
                db.rollback()

                current_app.logger.exception(
                    "Failed to generate recommendations"
                )

                abort(
                    503,
                    message=(
                        "MusicVault database temporarily unavailable"
                    ),
                )

        return {
            "items": items,
            "total": len(items),
        }