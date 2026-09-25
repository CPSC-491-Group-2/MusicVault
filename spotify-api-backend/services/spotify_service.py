import requests

class SpotifyService:
    def __init__(self, access_token:str):
        self.access_token = access_token
        self.headers = {
            "Authorization": f"Bearer {access_token}"
        }
        self.base_url = "https://api.spotify.com/v1"


    #retreive the current spotify user top track
    def get_user_top_track( #refer to Get User's top item in spotify api documentation
            self,
            limit =20, #how many result spotify return 
            time_range = "medium_term", #time frame using for compute
            offset = 0 #index of first item to return
    ):
        #validating parameters, make sure paramters was passed in correctly
        if limit < 1 or limit > 50:
                raise ValueError("limit must be between 1 and 50")
        valid_time_range ={
             "short_term", "medium_term", "long_term"
        }
        if time_range not in valid_time_range:
             raise ValueError("time range invalid")
        if offset <0:
             raise ValueError("offset must be greater than 0")
        #construct endpoint
        endpoint = f"{self.base_url}/me/top/tracks"

        #building query parameters for calling the api
        params ={
             "limit": limit, 
             "time_range": time_range,
             "offset": offset
        }

        #GET Request
        response = requests.get(
             endpoint, 
             headers = self.headers,
             params = params,
             timeout = 10
        )
        #handle response and return JSON
        if response.status_code == 200:
            return response.json()

    #def search_track():
    
    #def get_track():
    
    #def get_artist():
