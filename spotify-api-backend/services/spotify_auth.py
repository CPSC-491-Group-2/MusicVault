import os 
import requests
from urllib.parse import urlencode
from dotenv import load_dotenv

load_dotenv()


class SpotifyAuthService:
    AUTH_URL = "https://accounts.spotify.com/authorize"
    TOKEN_URL = "https://accounts.spotify.com/api/token"


    def __init__(self):
        self.client_id = os.getenv('SPOTIFY_CLIENT_ID')
        self.client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
        self.redirect_url = os.getenv('SPOTIFY_REDIRECT_URL')

        if not self.client_id:
            raise ValueError("SPOTIFY_CLIENT_ID is not set")

        if not self.client_secret:
            raise ValueError("SPOTIFY_CLIENT_SECRET is not set")

        if not self.redirect_url:
            raise ValueError("SPOTIFY_REDIRECT_URL is not set")
    
    def get_authorization_url(self):
        params ={
            "response_type": "code",
            "client_id": self.client_id,
            "scope": "user-top-read",
            "redirect_url": self.redirect_url
        }
        return f"{self.AUTH_URL}?{urlencode(params)}"


auth_service = SpotifyAuthService()

print(auth_service.get_authorization_url())