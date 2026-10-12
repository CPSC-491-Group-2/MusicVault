from dataclasses import dataclass


@dataclass
class TrackMetadata:
    spotify_id: str 
    name: str
    artists: list[str]
    album_name: str|None
    album_id: str|None 
    release_date: str
    duration_ms: int
    explicit: bool
    spotify_url: str|None


@dataclass
class ArtistMetadata:
        spotify_id: str
        name: str
        genres: list[str]
        popularity: int|None
        spotify_url:str|None


    
