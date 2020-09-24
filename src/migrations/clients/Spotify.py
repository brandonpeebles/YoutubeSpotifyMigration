# refactor to take the printing logic out and into a helper file

import os, sys, time, json
import base64
import pickle
import requests
import urllib
from urllib.parse import urlencode
from datetime import datetime, timedelta
import webbrowser
from pprint import pprint
from colorama import Fore, Back, Style

from src.exceptions import RequestError
from src.migrations.clients.credentials.SpotifyCredentials import Credentials

class Client:
    """class containing methods for interacting with Apple Music API"""

    def __init__(self):
        print(Fore.BLUE + 'Initializing Spotify API client.' + Style.RESET_ALL)
        self.client = None
        self.secrets = None
        self.base_auth_URI = 'https://accounts.spotify.com/authorize?'
        self.creds = None

    # AUTHENTICATION
    def authenticate(self):
        """Set up and authenticate youtube client"""
        print('Running Authorization Code Flow.')
        
        # Disable OAuthlib's HTTPS verification when running locally.
        # *DO NOT* leave this option enabled in production.
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
        # Client config
        creds = None

        # The file spotify_token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        print('Checking local directory for existing creds...', end=" ")
        if os.path.exists('spotify_token.pickle'):
            print(Fore.GREEN + 'Creds located.' + Style.RESET_ALL)
            creds = self._load_creds()
        if not creds or creds.valid() is False:
            if creds and creds.expired() is True and creds.refresh_token() is not None:
                print(Fore.MAGENTA + 'Creds expired.' + Style.RESET_ALL)
                print('Refreshing token...', end=" ")
                creds.refresh() 
            else:
                print(Fore.MAGENTA + 'Creds not found.' + Style.RESET_ALL)
                creds = self._run_manual_auth_code_flow()
            # Save the credentials for the next run
            self._save_creds(creds)   
        self.creds = creds
        print(Fore.GREEN + 'Creds loaded.' + Style.RESET_ALL)
        print(Fore.GREEN + 'Spotify API client successfully initialized.\n' + Style.RESET_ALL)
        time.sleep(1)

    def _run_manual_auth_code_flow(self):
        """
        Wrapper method for Spotify's auth code flow
        Requres user to visit browser for auth code to obtain tokens
        Returns creds object
        """
        print('Running manual authentication.')
        self.secrets = self._load_secrets("./spotify_client_secret.json")
        auth_URI = self._get_auth_uri()
        auth_code = self._get_auth_code_from_redirectURL(auth_URI)
        creds_json = self._request_tokens(auth_code)
        return Credentials(creds_json, self._get_auth_header())


    def _load_secrets(self, client_secrets_file):
        """Load the client secrets file to the class object or raise error"""
        try:
            with open(client_secrets_file) as f:
                client_secrets = json.load(f)
        except:
            print(Style.BRIGHT + Back.RED + Fore.WHITE + '\nERROR:' + Style.RESET_ALL)
            print(Style.NORMAL + Fore.RED + 'Missing spotify_client_secret.json.' + Style.RESET_ALL)
            print(Style.NORMAL + Fore.RED + 'Please visit the link below and create a project to obtain your client id and secret:' + Style.RESET_ALL)
            print(Style.NORMAL + Fore.RED + 'https://developer.spotify.com/dashboard/applications' + Style.RESET_ALL)
            print(Style.NORMAL + Fore.RED + 'Once created, click EDIT SETTINGS and add https://example.com/callback as a redirect uri. Click save.' + Style.RESET_ALL)
            print(Style.NORMAL + Fore.RED + '\nAdd them the root directory of this program in a file named spotify_client_secret.json with the following format:\n.' + Style.RESET_ALL)
            with open("./spotify_client_secret_example.json", "r") as f:
                example = json.load(f)
                pprint(example)
        else:
            return client_secrets
    
    def _get_auth_uri(self):
        """
        Use the client secrets file to create the auth URI for the initial GET request.
        The user will navigate to this link and retreive the URL redirect.
        """
        payload = {
            'client_id': self.secrets['client_id'],
            'redirect_uri': self.secrets['redirect_uri'],
            'scope': self.secrets['scope'],
            'response_type': self.secrets['response_type']
        }
        return self.base_auth_URI + urlencode(payload)
    
    def _get_auth_code_from_redirectURL(self, auth_uri):
        """
        Open web browser and direct user to login page based on their secrets file.
        Prompt the user to copy and paste the URL from when they're redirected back into the terminal
        Parse out the auth_code and store it in class object
        """
        print('You will sent to your browser to authenticate this app.')
        time.sleep(2)
        print('Follow the instructions there, and then copy/paste the URL here once you are redirected.')
        print('The web page whose URL you need to copy should say Example Domain.')
        time.sleep(2)
        print(Fore.BLUE + 'Redirecting in 5 seconds...' + Style.RESET_ALL)
        time.sleep(5)
        webbrowser.open(auth_uri)
        redirectURI = input("Paste the URL you were redirected to after logging in: ")
        parsedURI = urllib.parse.urlparse(redirectURI)
        return urllib.parse.parse_qs(parsedURI.query)['code'][0]
        
    def _request_tokens(self, auth_code):
        """
        Get access and refresh tokens from Spotify API using auth_code.
        Return response as json
        """
        # params
        payload = {
            'grant_type': "authorization_code",
            'redirect_uri': self.secrets['redirect_uri'],
            'code': auth_code
        }
        headers = {
            'Authorization': self._get_auth_header(),
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        # make request
        response = requests.post('https://accounts.spotify.com/api/token', data=payload, headers=headers)
        return response.json()

    def _save_creds(self, creds):
        """Pickle and save the credentials for easy logins"""
        print('Creds saved to ./spotify_token.pickle for future usage.')
        with open('spotify_token.pickle', 'wb') as token:
            pickle.dump(creds, token)
        # add error handling?

    def _load_creds(self):
        """Unpickle the spotify_token and return the creds"""
        print('Loading spotify_token.pickle...', end=" ")
        with open('spotify_token.pickle', 'rb') as token:
            creds = pickle.load(token)
        return creds

    def _get_auth_header(self):
        """generate base64 encoded authorization header for http requests (Basic client_id:client_secret)"""
        encodedData = base64.b64encode(f"{self.secrets['client_id']}:{self.secrets['client_secret']}".encode()).decode('utf-8')
        return f"Basic {encodedData}"


    # API METHODS
    def get_search_result(self, track, artist):
        """
        Search for song by track and artist name.
        Return first result object or None
        """
        payload = {
            'query': f"track:{track} artist:{artist}",
            'type': "track",
            'limit': 1
        }
        request_url = "https://api.spotify.com/v1/search?" + urlencode(payload)
        payload = {
            'query': f"track:{artist} artist:{track}",
            'type': "track",
            'limit': 1
        }        
        request_url_artist_as_track = "https://api.spotify.com/v1/search?" + urlencode(payload)
        headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.creds.access_token()}"
        }
        # make get request to spotify api for track and artist name
        response = requests.get(request_url, headers=headers)
        # check for good request
        if response.status_code != 200:
            raise RequestError(response.status_code, response.text)
        results_json = response.json()['tracks']['items']
        # check if search results contained any songs
        if len(results_json) == 0:
            # One last attempt, using the artist var as track 
            # (in case where youtube title is Track - Artist instead of Artist - Track)
            response = requests.get(request_url_artist_as_track, headers=headers)
            if response.status_code != 200:
                raise RequestError(response.status_code, response.text)
            results_json = response.json()['tracks']['items']
            if len(results_json) == 0:
                return None
            else:
                return results_json[0]
        else:
            return results_json[0]
    
    def _get_user_id(self):
        """fetch spotify user id based on the access token"""
        headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.creds.access_token()}"
        }
        response = requests.get("https://api.spotify.com/v1/me", headers=headers)
        if response.status_code != 200:
            raise RequestError(response.status_code, response.text)
        return response.json()['id']

    
    def create_playlist(self, songs, playlist_name):
        """Create new empty playlist and return playlist_id"""
        payload = {
            'name': playlist_name
        }
        headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.creds.access_token()}"
        }
        request_url = f"https://api.spotify.com/v1/users/{self._get_user_id()}/playlists"
        response = requests.post(request_url, json=payload, headers=headers)
        if response.status_code not in [200, 201]:
            raise RequestError(response.status_code, response.text)
        return response.json()['id']

    def add_songs_to_playlist(self, songs, playlist_id):
        """
        Add song(s) from list by URI to playlist by playlist_id/
        Per spotify API limitation, can only add up to 100 at at time
        """
        print(f"Adding selected songs to playlist...", end=" ")
        # split list of songs into URI lists of 100 each max
        URI_lists = list(self._partition_URI_list(songs, 100))
        for URI_list in URI_lists:
            # set body payload as comma separated list
            payload = {
                'uris':  URI_list
            }
            headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.creds.access_token()}"
            }
            request_url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
            response = requests.post(request_url, json=payload, headers=headers)
            if response.status_code not in [200, 201]:
                print(Back.RED + Fore.WHITE + "FAILED" + Style.RESET_ALL)
                raise RequestError(response.status_code, response.text)
        print(Fore.GREEN + 'Success.' + Style.RESET_ALL)
        # return the newly created playlist URL
        return f"https://open.spotify.com/playlist/{playlist_id}"

    def _partition_URI_list(self, l, n):
        """helper: splits URI list into lists of max allowable size (n) for API"""
        # list (l) and max size (n)
        for i in range(0, len(l), n):
            yield l[i:i+n]
        