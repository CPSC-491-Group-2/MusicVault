import requests

from spotify.parsers import normalize_top_tracks


class SpotifyServiceError(RuntimeError):
    """Base exception for Spotify API request failures."""


class SpotifyAuthenticationError(SpotifyServiceError):
    """Spotify rejected the access token."""


class SpotifyPermissionError(SpotifyServiceError):
    """Spotify denied access to the requested resource."""


class SpotifyResourceNotFoundError(SpotifyServiceError):
    """The requested Spotify resource does not exist."""


class SpotifyRateLimitError(SpotifyServiceError):
    """Spotify's API rate limit was reached."""

    def __init__(self, retry_after=None):
        super().__init__("Spotify rate limit exceeded")
        self.retry_after = retry_after


class SpotifyService:
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.headers = {"Authorization": f"Bearer {access_token}"}
        self.base_url = "https://api.spotify.com/v1"

    # handle request code function

    def _request(self, endpoint: str, params=None):
        """Perform a Spotify API request and handle errors."""

        try:
            response = requests.get(
                endpoint,
                headers=self.headers,
                params=params,
                timeout=10,
            )
        except requests.RequestException as exc:
            raise SpotifyServiceError("Could not reach Spotify API") from exc

        if response.status_code == 200:
            try:
                return response.json()
            except ValueError as exc:
                raise SpotifyServiceError("Invalid JSON returned by Spotify") from exc

        if response.status_code == 401:
            raise SpotifyAuthenticationError("Spotify authentication failed")

        if response.status_code == 403:
            raise SpotifyPermissionError("Spotify permission denied")

        if response.status_code == 404:
            raise SpotifyResourceNotFoundError("Spotify resource not found")

        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After")

            raise SpotifyRateLimitError(retry_after=retry_after)

        raise SpotifyServiceError(
            f"Spotify request failed with status {response.status_code}"
        )

    # retreive the current spotify user top track
    def get_user_top_track(  # refer to Get User's top item in spotify api documentation
        self,
        limit=20,  # how many result spotify return
        time_range="medium_term",  # time frame using for compute
        offset=0,  # index of first item to return
    ):
        # validating parameters, make sure paramters was passed in correctly
        if limit < 1 or limit > 50:
            raise ValueError("limit must be between 1 and 50")
        valid_time_range = {"short_term", "medium_term", "long_term"}
        if time_range not in valid_time_range:
            raise ValueError("time range invalid")
        if offset < 0:
            raise ValueError("offset must be nonnegative")
        # construct endpoint
        endpoint = f"{self.base_url}/me/top/tracks"

        # building query parameters for calling the api
        params = {"limit": limit, "time_range": time_range, "offset": offset}

        # handle response
        return self._request(endpoint, params)

    def get_normalized_user_top_tracks(
        self,
        limit: int = 20,
        time_range: str = "medium_term",
        offset: int = 0,
    ) -> dict:
        """Retrieve and normalize the current user's top tracks."""

        spotify_response = self.get_user_top_track(
            limit=limit,
            time_range=time_range,
            offset=offset,
        )

        return normalize_top_tracks(spotify_response)

    def search_track(self, query: str, limit: int = 10):
        # validating query (no empty search allow)
        if not query or not query.strip():
            raise ValueError("empty query")

        # validating limit
        if limit < 1 or limit > 50:
            raise ValueError("limit must be between 1 and 50")
        # build endpoint (Spotify endpoint for search is: /search)
        endpoint = f"{self.base_url}/search"

        # build params
        params = {"q": query, "type": "track", "limit": limit}

        # handle response
        return self._request(endpoint, params)

    def get_track(self, track_id: str):
        if not track_id or not track_id.strip():
            raise ValueError("track_id cannot be empty")

        endpoint = f"{self.base_url}/tracks/{track_id}"

        return self._request(endpoint)

    def get_artist(self, artist_id: str):
        if not artist_id or not artist_id.strip():
            raise ValueError("artist_id cannot be empty")
        endpoint = f"{self.base_url}/artists/{artist_id}"

        return self._request(endpoint)
