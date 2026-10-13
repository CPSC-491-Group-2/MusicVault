# MusicVault — Spotify Metadata Normalization

## Overview

MusicVault converts Spotify API track data into a consistent internal response format.

Normalization is implemented in `spotify/parsers.py` using two functions:

- `normalize_track(track)` — normalizes a single Spotify track.
- `normalize_top_tracks(response)` — normalizes a Spotify user's top-tracks response, including pagination metadata.

The normalized data is returned through the MusicVault backend endpoint:

`GET /api/v1/spotify/top-tracks`

## Normalized Track Schema

Example normalized track:

```json
{
  "spotify_id": "track123",
  "title": "Example Song",
  "artists": [
    {
      "spotify_id": "artist123",
      "name": "Example Artist"
    }
  ],
  "album": {
    "spotify_id": "album123",
    "name": "Example Album",
    "image_url": "https://example.com/album.jpg"
  },
  "duration_ms": 215000,
  "popularity": 75,
  "explicit": false,
  "spotify_url": "https://open.spotify.com/track/track123"
}
```

This is illustrative data rather than an actual Spotify API response.

## Field Mapping

| Spotify field | MusicVault field | Behavior |
|---|---|---|
| `id` | `spotify_id` | Required |
| `name` | `title` | Required |
| `artists[].id` | `artists[].spotify_id` | Required for each artist |
| `artists[].name` | `artists[].name` | Required for each artist |
| `album.id` | `album.spotify_id` | Optional; `null` if missing |
| `album.name` | `album.name` | Optional; `null` if missing |
| `album.images[].url` | `album.image_url` | First usable image URL, otherwise `null` |
| `duration_ms` | `duration_ms` | Optional; `null` if missing |
| `popularity` | `popularity` | Optional; `null` if missing |
| `explicit` | `explicit` | Defaults to `false` if missing or `null` |
| `external_urls.spotify` | `spotify_url` | Optional; `null` if missing |

The normalizer retains all artists in their original order. An empty artist list is permitted.

Additional Spotify fields not listed above are omitted from the normalized track.

## Normalized Top-Tracks Response

Example response:

```json
{
  "items": [
    {
      "spotify_id": "track123",
      "title": "Example Song",
      "artists": [
        {
          "spotify_id": "artist123",
          "name": "Example Artist"
        }
      ],
      "album": {
        "spotify_id": "album123",
        "name": "Example Album",
        "image_url": null
      },
      "duration_ms": 215000,
      "popularity": 75,
      "explicit": false,
      "spotify_url": null
    }
  ],
  "total": 50,
  "limit": 20,
  "offset": 0,
  "next": null,
  "previous": null
}
```

### Pagination Fields

| Field | Behavior |
|---|---|
| `items` | List of normalized tracks |
| `total` | Spotify's total value, or the number of returned items if missing |
| `limit` | Spotify's limit value, or the number of returned items if missing |
| `offset` | Spotify's offset value, or `0` if missing |
| `next` | Spotify's next-page URL, or `null` |
| `previous` | Spotify's previous-page URL, or `null` |

The endpoint accepts `limit`, `offset`, and `time_range` query parameters.

- `limit`: 1–50, default 20.
- `offset`: nonnegative integer, default 0.
- `time_range`: `short_term`, `medium_term`, or `long_term`; default `medium_term`.

## Validation and Missing Data

The normalizer raises `ValueError` when:

- A track is not a dictionary.
- A track lacks an ID or title.
- Album data is not a dictionary.
- Artist data is not a list.
- An artist is not a dictionary.
- An artist lacks an ID or name.
- The top-tracks response is not a dictionary.
- The top-tracks `items` field is not a list.

Missing or `null` album data becomes an object with nullable fields.

Missing or `null` artist data becomes an empty list.

Album images are inspected in order. The first image object containing a truthy `url` is selected. If none is found, `image_url` is `null`.

## Audio-Feature Metadata

The current implementation normalizes track metadata only.

Spotify audio-feature fields such as tempo, energy, danceability, and valence are not included in this schema. Supporting them would require an additional data source or response mapping and an agreed internal schema.

## Related Implementation Files

- `spotify/parsers.py` — track normalization.
- `services/spotify_service.py` — Spotify API requests and normalized top-tracks service.
- `../backend/app/schemas/spotify.py` — Flask response schemas.
- `../backend/app/routes/spotify.py` — authenticated top-tracks endpoint.
