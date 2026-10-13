#translating sptoify response into models

from spotify.models import TrackMetadata, ArtistMetadata

def parse_track(track_data: dict) -> TrackMetadata:
    artists = track_data.get('artists', [])

    album = track_data.get('album') or {}

    images = album.get('images') or []
    
    external_urls = track_data.get('external_urls') or {}

    return TrackMetadata(
        spotify_id =track_data.get('id',''),
        name = track_data.get('name', ''),
        artists=[
            artist.get('name','')
            for artist in artists
        ],
        artist_ids=[
            artist.get('id','')
            for artist in artists
        ],
        album_name = album.get('name'),
        album_id = album.get('id'),
        release_date = album.get('release_date'),
        duration_ms =track_data.get('duration_ms'),
        explicit=track_data.get('explicit', False),
        spotify_url = external_urls.get('spotify'),
        image_url = images[0].get('url') if images else None 
    )