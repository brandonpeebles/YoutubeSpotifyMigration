import json
from pprint import pprint
import requests
from datetime import datetime, timedelta

class Credentials:
    """Class for storing and interacting with Spotify OAuth2 credentials"""
    def __init__(self, creds_json, auth_header):
        """initialize credentials object with creds and base64 encoded auth_header and add expiry."""
        self._access_token = creds_json['access_token']
        self._token_type = creds_json['token_type']
        self._expires_in = creds_json['expires_in']
        self._expiry = datetime.now() + timedelta(seconds=creds_json['expires_in'])
        self._refresh_token = creds_json['refresh_token']
        self._scope = creds_json['scope']
        self._auth_header = auth_header
        
    def access_token(self):
        """getter for access_token"""
        return self._access_token
    
    def refresh_token(self):
        """getter for refresh_token"""
        return self._refresh_token

    def auth_header(self):
        """getter for auth_header"""
        return self._auth_header

    def _set_expiry(self, expires_in):
        """setter for expiry"""
        self._expiry = datetime.now() + timedelta(seconds=expires_in)
    
    def expired(self):
        """Returns true if current access token is expired. False otherwise."""
        return datetime.now() > self._expiry

    def valid(self):
        """Returns true if tokens exist and are not expired. False otherwise."""
        if self._access_token and self._refresh_token and self.expired() is False:
            return True
        else:
            return False

    def refresh(self, auth_header: str):
        """Requests refreshed access token using the refresh_token and updates existing"""
        payload = {
            'grant_type': "refresh_token",
            'refresh_token': self._refresh_token
        }
        headers = {
            'Authorization': self._auth_header,
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        # make request
        response = requests.post('https://accounts.spotify.com/api/token', data=payload, headers=headers)
        response = json.loads(response.text)
        # update creds with new data from response
        self._access_token = response['access_token']
        self._set_expiry(response['expires_in'])