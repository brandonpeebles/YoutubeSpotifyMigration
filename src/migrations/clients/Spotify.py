# refactor to take the printing logic out and into a helper file

import os, sys, time, json
import base64
import pickle
import requests
import urllib
from urllib.parse import urlencode
import webbrowser
from pprint import pprint
from colorama import Fore, Back, Style

from src.exceptions import RequestError

class Client:
    """class containing methods for interacting with Apple Music API"""

    def __init__(self):
        print(Fore.BLUE + 'Initializing Spotify API client.' + Style.RESET_ALL)
        self.client = None
        self.secrets = None
        self.base_auth_URI = 'https://accounts.spotify.com/authorize?'
        self.auth_code = None
        self.creds = None

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
            print('Loading spotify_token.pickle...', end=" ")
            with open('spotify_token.pickle', 'rb') as token:
                creds = pickle.load(token)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                print(Fore.MAGENTA + 'Creds expired.' + Style.RESET_ALL)
                print('Refreshing token...', end=" ")
                # creds.refresh(Request()) <---- replace me
            else:
                print(Fore.MAGENTA + 'Creds not found.' + Style.RESET_ALL)
                print('Running manual authentication.')
                time.sleep(2)
                self._load_secrets()
                self._get_auth_code_from_redirectURL(self._get_auth_uri())
                creds = self._request_tokens()


                # pprint(response.text)
                # except:
                #     pass
                # except:
                #     print(Style.BRIGHT + Back.RED + Fore.WHITE + '\nERROR:' + Style.RESET_ALL)
                #     print(Style.NORMAL + Fore.RED + 'Missing client_secrets_file.json.' + Style.RESET_ALL)
                #     print(Style.NORMAL + Fore.RED + 'Please visit the link below and follow Step 1 to obtain these credentials:' + Style.RESET_ALL)
                #     print(Style.NORMAL + Fore.RED + 'https://developers.google.com/youtube/v3/quickstart/python#step_1_set_up_your_project_and_credentials' + Style.RESET_ALL)
                #     print(Style.NORMAL + Fore.RED + '\nAdd them the root directory of this program in a file named client_secret.json with the following format:\n.' + Style.RESET_ALL)
                #     with open("./youtube_client_secret_example.json", "r") as f:
                #         example = json.load(f)
                #         pprint(example)
                # else:
                #     try:
                #         # creds = flow.run_local_server(port=1) # not working
                #         creds = flow.run_console()
                #     except:
                #         print(Style.BRIGHT + Back.RED + Fore.WHITE + '\nERROR:' + Style.RESET_ALL)
                #         print(Style.NORMAL + Fore.RED + 'Failed to authenticate. Please try again.\n' + Style.RESET_ALL)
                #         # creds = flow.run_local_server(port=1) 
                #         creds = flow.run_console()
                #     else:
                #         print(Fore.GREEN + 'Successfully authenticated!' + Style.RESET_ALL)
                #     # Save the credentials for the next run
                #     print(Fore.YELLOW + 'Creds saved to ./spotify_token.pickle for future usage.' + Style.RESET_ALL)
                #     with open('spotify_token.pickle', 'wb') as token:
                #         pickle.dump(creds, token)
                # print(Fore.GREEN + 'Creds loaded.' + Style.RESET_ALL)
    def _load_secrets(self):
        """Load the client secrets file to the class object or raise error"""
        client_secrets_file = "./spotify_client_secret.json"
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
            self.secrets = client_secrets

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
        print('You will sent to a spotify login page to authenticate this app. Log in, do not close the page, and come back here.')
        print(Fore.BLUE + 'Redirecting in 5 seconds...' + Style.RESET_ALL)
        time.sleep(5)
        webbrowser.open(auth_uri)
        redirectURI = input("Paste the URL you were redirected to after logging in: ")
        parsedURI = urllib.parse.urlparse(redirectURI)
        self.auth_code = urllib.parse.parse_qs(parsedURI.query)['code'][0]
        
    def _request_tokens(self):
        """get access and refresh tokens from Spotify API using auth_code"""
        # params
        payload = {
            'grant_type': "authorization_code",
            'redirect_uri': self.secrets['redirect_uri'],
            'code': self.auth_code
        }
        # auth header
        encodedData = base64.b64encode(f"{self.secrets['client_id']}:{self.secrets['client_secret']}".encode()).decode('utf-8')
        authorization_header_string = f"Basic {encodedData}"
        headers = {
            'Authorization': authorization_header_string,
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        # request
        response = requests.post('https://accounts.spotify.com/api/token', data=payload, headers=headers)
        creds = json.loads(response.text)
        return creds
    
    def _refresh_token(self):
        """Request new token to replace expired one"""
        pass

    