"""Spotify API request and response schemas for MusicVault."""

from marshmallow import Schema, fields, validate


class SpotifyTopTracksQuerySchema(Schema):
    """Validate parameters for the Spotify top-tracks endpoint."""

    time_range = fields.String(
        load_default="medium_term",
        validate=validate.OneOf(["short_term", "medium_term", "long_term"]),
        metadata={"description": "Spotify listening history range"},
    )

    limit = fields.Integer(
        load_default=20,
        validate=validate.Range(min=1, max=50),
        metadata={"description": "Number of tracks to return"},
    )

    offset = fields.Integer(
        load_default=0,
        validate=validate.Range(min=0),
        metadata={"description": "Pagination offset"},
    )


class SpotifyArtistSchema(Schema):
    spotify_id = fields.String(required=True)
    name = fields.String(required=True)


class SpotifyAlbumSchema(Schema):
    spotify_id = fields.String(allow_none=True)
    name = fields.String(allow_none=True)
    image_url = fields.Url(allow_none=True)


class SpotifyTrackSchema(Schema):
    spotify_id = fields.String(required=True)
    title = fields.String(required=True)
    artists = fields.List(
        fields.Nested(SpotifyArtistSchema),
        required=True,
    )
    album = fields.Nested(
        SpotifyAlbumSchema,
        required=True,
    )
    duration_ms = fields.Integer(allow_none=True)
    popularity = fields.Integer(allow_none=True)
    explicit = fields.Boolean(required=True)
    spotify_url = fields.Url(allow_none=True)


class SpotifyTopTracksResponseSchema(Schema):
    items = fields.List(
        fields.Nested(SpotifyTrackSchema),
        required=True,
    )
    total = fields.Integer(required=True)
    limit = fields.Integer(required=True)
    offset = fields.Integer(required=True)
    next = fields.Url(allow_none=True)
    previous = fields.Url(allow_none=True)
