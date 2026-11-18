# Swipe Deck Contract

The JSON contract for the swipe deck endpoints. Neither endpoint is implemented yet; this document is the specification a later chunk builds them to, and the contract a frontend developer can build the swipe deck UI against today using the mock response below, with no backend running. The scoring behind `score` and `components` is described in [similarity-scoring.md](similarity-scoring.md).

## `GET /api/v1/swipe/deck`

Requires a logged-in user. Returns a page of candidate songs to show in the swipe deck.

### Query parameters

| Parameter | Type | Default | Notes |
|---|---|---|---|
| `limit` | integer | 10 | Max 50. Number of items to return. |
| `exclude` | string | (none) | Comma-separated song IDs already seen this session, so they are not returned again. |

### Response 200

```json
{
  "items": [
    {
      "song": {
        "id": "a1b2c3d4-0001-4000-8000-000000000001",
        "title": "Overgrown",
        "artist": "Fenne Lily",
        "album": "BREACH",
        "album_image_url": "https://i.scdn.co/image/ab67616d0000b273a1b2c3d4e5f6a7b8c9d0e1f2",
        "preview_url": "https://cdnt-preview.dzcdn.net/api/1/1/8/f/2/0/8f2e1a9b7c3d4e5f6a7b8c9d0e1f2a3b.mp3?hdnea=exp=1763330400~acl=/api/1/1*~hmac=4f3e2d1c0b9a8f7e6d5c4b3a2f1e0d9c",
        "spotify_url": "https://open.spotify.com/track/5ChkMS8OtdzJeqyybCc9R5"
      },
      "reason": {
        "text": "Because you keep Lucy Dacus, who tours with Fenne Lily",
        "path": ["Lucy Dacus", "Fenne Lily"]
      },
      "score": 0.87,
      "components": { "graph": 0.9, "similarity": 0.81, "discovery": 0.72 }
    },
    {
      "song": {
        "id": "a1b2c3d4-0002-4000-8000-000000000002",
        "title": "Glue Song",
        "artist": "beabadoobee",
        "album": "Beatopia",
        "album_image_url": "https://i.scdn.co/image/ab67616d0000b273b2c3d4e5f6a7b8c9d0e1f2a",
        "preview_url": "https://cdnt-preview.dzcdn.net/api/1/1/3/d/9/0/3d9f8e7c6b5a4f3e2d1c0b9a8f7e6d5c.mp3?hdnea=exp=1763330400~acl=/api/1/1*~hmac=9c8b7a6f5e4d3c2b1a0f9e8d7c6b5a4f",
        "spotify_url": "https://open.spotify.com/track/2tcaB0eyI0C57g39Kyp5OE"
      },
      "reason": {
        "text": "Shares a tempo and mood with songs you saved",
        "path": ["Clairo", "beabadoobee"]
      },
      "score": 0.74,
      "components": { "graph": 0.55, "similarity": 0.88, "discovery": 0.65 }
    },
    {
      "song": {
        "id": "a1b2c3d4-0003-4000-8000-000000000003",
        "title": "Kyoto",
        "artist": "Phoebe Bridgers",
        "album": "Punisher",
        "album_image_url": "https://i.scdn.co/image/ab67616d0000b273c3d4e5f6a7b8c9d0e1f2a3b",
        "preview_url": "https://cdnt-preview.dzcdn.net/api/1/1/7/a/1/5/7a15c4d3e2f1a0b9c8d7e6f5a4b3c2d1.mp3?hdnea=exp=1763330400~acl=/api/1/1*~hmac=1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d",
        "spotify_url": "https://open.spotify.com/track/4SOMwtAKIaFFbBhRcyjJx1"
      },
      "reason": {
        "text": "A less-streamed pick from an artist adjacent to your top genre",
        "path": ["boygenius", "Phoebe Bridgers"]
      },
      "score": 0.61,
      "components": { "graph": 0.4, "similarity": 0.52, "discovery": 0.91 }
    }
  ],
  "algorithm_version": "swipe-v1"
}
```

`song` reuses the field names returned by the rest of the API: `id`, `title`, `artist`, `album`, `album_image_url`, `spotify_url`. `preview_url` is new in this endpoint; see the limitation below before wiring up audio playback.

Only `id`, `title` and `artist` are always present. `album`, `album_image_url`, `spotify_url` and `preview_url` are each nullable and must be rendered defensively: a song reached through the artist graph may have no Spotify match, and a song with no licensed preview has `preview_url: null`. Treat a null `preview_url` as "not playable" rather than hiding the card.

`score` and each value in `components` (`graph`, `similarity`, `discovery`) are floats in `0..1`. `reason.path` lists the artist names describing the graph hop that produced the recommendation, in order, starting from an artist the listener already likes and ending at the recommended song's artist; `reason.text` is a short sentence for display in the UI.

### `preview_url` is perishable

`preview_url` is a signed, time-limited Deezer CDN URL. It expires within hours, and its signature cannot be stripped or reconstructed to extend it. Clients must not cache a `preview_url` or persist it beyond the current session, and must handle a failed audio load (expired link, network error) gracefully, for example by disabling the play button or falling back to `spotify_url`. Re-fetching the deck gets fresh URLs.

## `POST /api/v1/swipe`

Requires a logged-in user. Records a swipe action as a user preference.

### Request body

```json
{
  "song_id": "a1b2c3d4-0001-4000-8000-000000000001",
  "action": "keep",
  "deck_position": 0
}
```

| Field | Type | Notes |
|---|---|---|
| `song_id` | string | ID of the song being swiped. |
| `action` | string | One of exactly `keep`, `pass`, `skip`. |
| `deck_position` | integer | Index of the card in the current deck, for analytics. |

### Response 200

```json
{
  "song_id": "a1b2c3d4-0001-4000-8000-000000000001",
  "preference_type": "liked"
}
```

`preference_type` is the stored preference value, as described in [recommendation-data-integrity.md](recommendation-data-integrity.md#preferences). Each `action` maps to exactly one of them:

| `action` | stored `preference_type` | Meaning |
|---|---|---|
| `keep` | `liked` | The listener kept the song. |
| `pass` | `disliked` | The listener rejected the song. |
| `skip` | `skipped` | The listener moved on without judging it. |

`saved` and `neutral` are part of the preference vocabulary but are not produced by this endpoint.

## Errors

Both endpoints follow the API's [error format](../README.md#error-format):

```json
{
  "error": "Unauthorized",
  "message": "You must be logged in to access this resource.",
  "code": "unauthorized"
}
```

A logged-out caller gets `401` with `code: "unauthorized"` on both endpoints; a session issued before the user's password last changed gets the same status with `code: "session_revoked"`. `POST /api/v1/swipe` with an unknown `song_id` gets `404`, whose body has no `code` key. A missing `song_id` or an `action` outside `keep`/`pass`/`skip` fails flask-smorest's own request validation, which returns a different envelope, `{"code": <int>, "status": "...", "message": "..."}`, where `code` is the numeric HTTP status rather than a string slug, so clients must not assume `code` is always a string.
