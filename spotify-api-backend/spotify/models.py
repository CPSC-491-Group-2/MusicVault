"""Spotify metadata models."""

from dataclasses import dataclass


@dataclass
class TrackMetadata:
    spotify_id: str
    name: str
    artists: list[str]
    artist_ids: list[str]
    album_name: str | None
    album_id: str | None
    release_date: str | None
    duration_ms: int | None
    explicit: bool
    spotify_url: str | None
    image_url: str | None


@dataclass
class ArtistMetadata:
    spotify_id: str
    name: str
    genres: list[str]
    popularity: int | None
    spotify_url: str | None
