from __future__ import annotations

import uuid

from sqlalchemy import delete, func, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models.artist import Artist, ArtistEdge, ArtistExternalId, SongArtist
from models.song import Song


def upsert_artist_from_deezer(db: Session, artist: dict) -> uuid.UUID:
    """Store a normalized Deezer artist and return the canonical artist id.

    The Deezer id is matched through artist_external_ids, so an artist already
    known from another provider keeps its row. A payload without a fan count
    (a chart entry, for example) leaves a previously stored count alone rather
    than erasing it.
    """
    deezer_id = (artist.get("deezer_id") or "").strip()
    name = (artist.get("name") or "").strip()
    if not deezer_id:
        raise ValueError(
            f"artist deezer_id is required (got {artist.get('deezer_id')!r})"
        )
    if not name:
        raise ValueError(f"artist name is required (got {artist.get('name')!r})")

    artist_id = _deezer_artist_id(db, deezer_id)
    if artist_id is None:
        try:
            artist_id = _insert_artist(db, deezer_id, name)
        except IntegrityError:
            db.rollback()
            artist_id = _deezer_artist_id(db, deezer_id)
            if artist_id is None:
                raise

    values: dict = {"name": name, "updated_at": func.now()}
    if artist.get("fans") is not None:
        values["fans"] = artist["fans"]
        values["fans_source"] = "deezer"

    try:
        db.execute(update(Artist).where(Artist.id == artist_id).values(**values))
        db.commit()
    except Exception:
        db.rollback()
        raise
    return artist_id


def upsert_song_from_deezer(db: Session, track: dict) -> uuid.UUID:
    """Store a normalized Deezer track with its credits and return the song id.

    A song already imported from Spotify is adopted by ISRC instead of being
    duplicated. Fields Deezer did not supply keep their stored value, except
    preview_url, which is always refreshed because Deezer's previews expire.
    """
    deezer_id = (track.get("deezer_id") or "").strip()
    title = (track.get("title") or "").strip()
    if not deezer_id:
        raise ValueError(
            f"track deezer_id is required (got {track.get('deezer_id')!r})"
        )
    if not title:
        raise ValueError(f"track title is required (got {track.get('title')!r})")
    if not track.get("artists"):
        raise ValueError(f"track {deezer_id!r} has no credited artists")

    credits: list[tuple[uuid.UUID, str]] = []
    seen: set[uuid.UUID] = set()
    for entry in track.get("artists") or []:
        artist_id = upsert_artist_from_deezer(db, entry)
        if artist_id not in seen:
            seen.add(artist_id)
            credits.append((artist_id, entry["name"].strip()))

    isrc = track.get("isrc")
    song_id = db.scalar(select(Song.id).where(Song.deezer_track_id == deezer_id))
    if song_id is None and isrc:
        # Only adopt a row with no Deezer identity yet, or two Deezer tracks sharing
        # an ISRC would take turns stealing each other's row. The lock makes Postgres
        # re-check that predicate once a competing adopter commits, so the loser
        # finds nothing and inserts its own row instead of overwriting.
        song_id = db.scalar(
            select(Song.id)
            .where(Song.isrc == isrc, Song.deezer_track_id.is_(None))
            .order_by(Song.created_at)
            .limit(1)
            .with_for_update()
        )

    values: dict = {
        "title": title,
        "artist_name": ", ".join(name for _, name in credits),
        "album_name": track.get("album_name"),
        "duration_ms": track.get("duration_ms"),
        "explicit": track.get("explicit"),
        "preview_url": track.get("preview_url"),
        "deezer_track_id": deezer_id,
    }
    if isrc:
        values["isrc"] = isrc
    if track.get("album_image_url"):
        values["album_image_url"] = track["album_image_url"]

    try:
        if song_id is None:
            song_id = db.scalar(insert(Song).values(**values).returning(Song.id))
        else:
            db.execute(
                update(Song)
                .where(Song.id == song_id)
                .values(**values, updated_at=func.now())
            )
        _set_credits(db, song_id, [artist_id for artist_id, _ in credits])
        db.commit()
    except Exception:
        db.rollback()
        raise
    return song_id


def upsert_edge(
    db: Session,
    *,
    src_artist_id: uuid.UUID,
    dst_artist_id: uuid.UUID,
    provider: str,
    weight: float,
) -> None:
    if src_artist_id == dst_artist_id:
        raise ValueError(f"an artist cannot be similar to itself ({src_artist_id!r})")
    if not 0 <= weight <= 1:
        raise ValueError(f"weight must be between 0 and 1 (got {weight!r})")

    statement = insert(ArtistEdge).values(
        src_artist_id=src_artist_id,
        dst_artist_id=dst_artist_id,
        provider=provider,
        weight=weight,
    )
    db.execute(
        statement.on_conflict_do_update(
            index_elements=["src_artist_id", "dst_artist_id", "provider"],
            set_={"weight": statement.excluded.weight, "fetched_at": func.now()},
        )
    )
    db.commit()


def mark_expanded(db: Session, artist_id: uuid.UUID) -> None:
    db.execute(
        update(Artist)
        .where(Artist.id == artist_id)
        .values(last_expanded_at=func.now(), updated_at=func.now())
    )
    db.commit()


def catalog_counts(db: Session) -> dict[str, int]:
    models = {
        "artists": Artist,
        "songs": Song,
        "song_artists": SongArtist,
        "artist_external_ids": ArtistExternalId,
        "artist_edges": ArtistEdge,
    }
    return {
        name: db.scalar(select(func.count()).select_from(model))
        for name, model in models.items()
    }


def _deezer_artist_id(db: Session, deezer_id: str) -> uuid.UUID | None:
    return db.scalar(
        select(ArtistExternalId.artist_id).where(
            ArtistExternalId.provider == "deezer",
            ArtistExternalId.external_id == deezer_id,
        )
    )


def _insert_artist(db: Session, deezer_id: str, name: str) -> uuid.UUID:
    """Add the artist and its Deezer link; raises IntegrityError if one exists."""
    artist_id = db.scalar(insert(Artist).values(name=name).returning(Artist.id))
    db.execute(
        insert(ArtistExternalId).values(
            artist_id=artist_id, provider="deezer", external_id=deezer_id
        )
    )
    return artist_id


def _set_credits(db: Session, song_id: uuid.UUID, artist_ids: list[uuid.UUID]) -> None:
    db.execute(delete(SongArtist).where(SongArtist.song_id == song_id))
    for position, artist_id in enumerate(artist_ids, start=1):
        db.execute(
            insert(SongArtist).values(
                song_id=song_id, artist_id=artist_id, position=position
            )
        )
