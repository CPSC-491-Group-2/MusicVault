import logging
import time

import requests

from ..pacing import TokenBucket

log = logging.getLogger("crawler.deezer")


class DeezerError(Exception):
    pass


class DeezerQuotaError(DeezerError):
    pass


class DeezerDataError(DeezerError):
    pass


class DeezerClient:
    def __init__(
        self,
        limiter: TokenBucket,
        session: requests.Session | None = None,
        base_url: str = "https://api.deezer.com",
        timeout: float = 10.0,
    ) -> None:
        self._limiter = limiter
        self._session = session or requests.Session()
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    def chart_artists(self, limit: int = 50) -> list[dict]:
        payload = self._get("/chart/0/artists", {"limit": limit})
        return [_artist(item) for item in payload.get("data", [])]

    def artist(self, artist_id: str) -> dict:
        return _artist(self._get(f"/artist/{artist_id}"))

    def related_artists(self, artist_id: str, limit: int = 20) -> list[dict]:
        payload = self._get(f"/artist/{artist_id}/related", {"limit": limit})
        return [_artist(item) for item in payload.get("data", [])]

    def top_tracks(self, artist_id: str, limit: int = 25) -> list[dict]:
        payload = self._get(f"/artist/{artist_id}/top", {"limit": limit})
        return [_track(item) for item in payload.get("data", [])]

    def track(self, track_id: str) -> dict:
        return _track(self._get(f"/track/{track_id}"))

    def _get(self, path: str, params: dict | None = None) -> dict:
        self._limiter.acquire()
        started = time.monotonic()
        try:
            response = self._session.get(
                self._base_url + path, params=params, timeout=self._timeout
            )
        except requests.RequestException as exc:
            raise DeezerError(f"request failed for path={path}: {exc}") from exc
        elapsed_ms = int((time.monotonic() - started) * 1000)
        log.info(
            "deezer request path=%s status=%s elapsed_ms=%s",
            path,
            response.status_code,
            elapsed_ms,
        )
        if response.status_code != 200:
            raise DeezerError(
                f"unexpected status {response.status_code} for path={path}"
            )
        try:
            payload = response.json()
        except ValueError as exc:
            raise DeezerError(f"non-JSON body for path={path}: {exc}") from exc
        # Deezer answers HTTP 200 with an {"error": ...} body instead of a failure status.
        error = payload.get("error") if isinstance(payload, dict) else None
        if error:
            raise _error_for(error, path)
        return payload


def _error_for(error: dict, path: str) -> DeezerError:
    kind = error.get("type")
    code = error.get("code")
    message = error.get("message", "")
    detail = f"{kind or code} for path={path}: {message}"
    if kind == "QuotaException" or code == 4:
        return DeezerQuotaError(detail)
    return DeezerDataError(detail)


def _artist(item: dict) -> dict:
    return {
        "deezer_id": _identifier(item, "artist"),
        "name": item.get("name"),
        "fans": item.get("nb_fan"),
        "picture_url": item.get("picture_xl") or item.get("picture_big") or None,
        "link": item.get("link") or None,
    }


def _identifier(item: dict, kind: str) -> str:
    value = item.get("id")
    if value is None:
        raise DeezerDataError(f"{kind} payload has no id: {sorted(item)}")
    return str(value)


def _track(item: dict) -> dict:
    album = item.get("album") or {}
    duration = item.get("duration")
    return {
        "deezer_id": _identifier(item, "track"),
        "title": item.get("title"),
        "isrc": item.get("isrc") or None,
        "duration_ms": duration * 1000 if duration is not None else None,
        "explicit": item.get("explicit_lyrics"),
        "preview_url": item.get("preview") or None,
        "link": item.get("link") or None,
        "album_name": album.get("title"),
        "album_image_url": album.get("cover_xl") or album.get("cover_big") or None,
        "artists": _credits(item),
    }


def _credits(item: dict) -> list[dict]:
    contributors = item.get("contributors") or []
    if not contributors:
        single = item.get("artist")
        contributors = [single] if single else []
    return [
        {"deezer_id": _identifier(c, "artist"), "name": c.get("name")}
        for c in contributors
    ]
