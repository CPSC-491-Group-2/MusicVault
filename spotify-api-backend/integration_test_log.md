# Spotify API integration test log 
```
(.venv) minhcranel@minhcranel-Latitude-3301:~/Documents/projects/MusicVault/spotify-api-backend$ python -m pytest tests/integration/test_spotify_integration.py -v -s
===================================================== test session starts ======================================================
platform linux -- Python 3.12.3, pytest-9.1.1, pluggy-1.6.0 -- /home/minhcranel/Documents/projects/MusicVault/spotify-api-backend/.venv/bin/python
cachedir: .pytest_cache
rootdir: /home/minhcranel/Documents/projects/MusicVault/spotify-api-backend
collected 1 item                                                                                                               

tests/integration/test_spotify_integration.py::test_live_search_track_and_retrieve_details PASSED

======================================================= warnings summary =======================================================
tests/integration/test_spotify_integration.py:10
  /home/minhcranel/Documents/projects/MusicVault/spotify-api-backend/tests/integration/test_spotify_integration.py:10: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
================================================= 1 passed, 1 warning in 1.42s =================================================
(.venv) minhcranel@minhcranel-Latitude-3301:~/Documents/projects/MusicVault/spotify-api-backend$ curl -i \
  -H "Authorization: Bearer $SPOTIFY_ACCESS_TOKEN" \
  "https://api.spotify.com/v1/search?q=Lose%20Yourself&type=track&limit=1"
HTTP/2 200 
content-type: application/json; charset=utf-8
cache-control: public, max-age=0
etag: "MC-IjMzZDM3NmYxMzY0OTdhN2UzMTgzMmI4OWMyMzMzOTNhIg=="
mc-cache-ttl: 7200
mc-cache-policy: public
x-robots-tag: noindex, nofollow
mc-etag: "33d376f136497a7e31832b89c233393a"
content-length: 2238
server-timing: edge;dur=305
strict-transport-security: max-age=31536000
x-content-type-options: nosniff
alt-svc: h3=":443"; ma=2592000,h3-29=":443"; ma=2592000
alt-svc: h3=":443"; ma=2592000
vary: Accept-Encoding
date: Sun, 11 Oct 2026 08:01:42 GMT
server: envoy
via: HTTP/2 edgeproxy, 1.1 google

{"tracks":{"href":"https://api.spotify.com/v1/search?offset=0&limit=1&query=Lose%20Yourself&type=track","limit":1,"next":"https://api.spotify.com/v1/search?offset=1&limit=1&query=Lose%20Yourself&type=track","offset":0,"previous":null,"total":390,"items":[{"album":{"album_type":"album","artists":[{"external_urls":{"spotify":"https://open.spotify.com/artist/4tZwfgrHOc3mvqYlEYSvVi"},"href":"https://api.spotify.com/v1/artists/4tZwfgrHOc3mvqYlEYSvVi","id":"4tZwfgrHOc3mvqYlEYSvVi","name":"Daft Punk","type":"artist","uri":"spotify:artist:4tZwfgrHOc3mvqYlEYSvVi"}],"external_urls":{"spotify":"https://open.spotify.com/album/4m2880jivSbbyEGAKfITCa"},"href":"https://api.spotify.com/v1/albums/4m2880jivSbbyEGAKfITCa","id":"4m2880jivSbbyEGAKfITCa","images":[{"height":640,"width":640,"url":"https://i.scdn.co/image/ab67616d0000b2739b9b36b0e22870b9f542d937"},{"height":300,"width":300,"url":"https://i.scdn.co/image/ab67616d00001e029b9b36b0e22870b9f542d937"},{"height":64,"width":64,"url":"https://i.scdn.co/image/ab67616d000048519b9b36b0e22870b9f542d937"}],"is_playable":true,"name":"Random Access Memories","release_date":"2013-05-20","release_date_precision":"day","total_tracks":13,"type":"album","uri":"spotify:album:4m2880jivSbbyEGAKfITCa"},"artists":[{"external_urls":{"spotify":"https://open.spotify.com/artist/4tZwfgrHOc3mvqYlEYSvVi"},"href":"https://api.spotify.com/v1/artists/4tZwfgrHOc3mvqYlEYSvVi","id":"4tZwfgrHOc3mvqYlEYSvVi","name":"Daft Punk","type":"artist","uri":"spotify:artist:4tZwfgrHOc3mvqYlEYSvVi"},{"external_urls":{"spotify":"https://open.spotify.com/artist/2RdwBSPQiwcmiDo9kixcl8"},"href":"https://api.spotify.com/v1/artists/2RdwBSPQiwcmiDo9kixcl8","id":"2RdwBSPQiwcmiDo9kixcl8","name":"Pharrell Williams","type":"artist","uri":"spotify:artist:2RdwBSPQiwcmiDo9kixcl8"}],"disc_number":1,"duration_ms":353893,"explicit":false,"external_ids":{"isrc":"USQX91300106"},"external_urls":{"spotify":"https://open.spotify.com/track/5CMjjywI0eZMixPeqNd75R"},"href":"https://api.spotify.com/v1/tracks/5CMjjywI0eZMixPeqNd75R","id":"5CMjjywI0eZMixPeqNd75R","is_local":false,"is_playable":true,"name":"Lose Yourself to Dance (feat. Pharrell Williams)","track_number":6,"type":"track","uri":"spotify:track:5CMjjywI0eZMixPeqNd75R"}]}}
```