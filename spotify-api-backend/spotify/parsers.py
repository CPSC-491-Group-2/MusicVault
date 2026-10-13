#translating sptoify response into models

from spotify.models import TrackMetadata, ArtistMetadata

def parse_track(track_data: dict) -> TrackMetadata:
    artists = track_data.get('artist', [])

    album = track_data.get('album') or {}

    external_urls = track_data.get('external_urls') or {}

    return TrackMetadata(
        spotify_id =track_data.get('id',''),
        name = track_data.get('name', ''),
        artists=[
            artist.get('name','')
            for artist in artists
        ],
        
            
        

    )