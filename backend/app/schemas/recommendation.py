"""Recommendation API response schemas."""

from marshmallow import Schema, fields


class RecommendationItemSchema(Schema):
    id = fields.UUID(required=True)
    title = fields.String(required=True)
    artist = fields.String(required=True)
    album = fields.String(allow_none=True)

    spotify_track_id = fields.String(allow_none=True)
    spotify_url = fields.Url(allow_none=True)
    album_image_url = fields.Url(allow_none=True)

    popularity = fields.Integer(allow_none=True)

    score = fields.Float(required=True)
    reason = fields.String(allow_none=True)

    components = fields.Dict(
        keys=fields.String(),
        values=fields.Float(allow_none=True),
        required=True,
    )


class RecommendationResponseSchema(Schema):
    items = fields.List(
        fields.Nested(RecommendationItemSchema),
        required=True,
    )
    total = fields.Integer(required=True)