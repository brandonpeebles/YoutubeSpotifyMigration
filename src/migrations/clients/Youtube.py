# refactor to take the printing logic out and into a helper file

import os, sys, time, json
import pickle
from pprint import pprint
from colorama import Fore, Back, Style

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from google.auth.transport.requests import Request

from src.exceptions import RequestError

class Client:
    """class containing methods for interacting with Apple Music API"""

    def __init__(self):
        print(Fore.BLUE + 'Initializing Youtube API client.' + Style.RESET_ALL)
        self.client = None

    # AUTHENTICATION
    def authenticate(self):
        """Set up and authenticate youtube client"""
        print('Running OAuth script.')

        # Method below adapted from Google's example: 
        # https://developers.google.com/youtube/v3/quickstart/python
        # Disable OAuthlib's HTTPS verification when running locally.
        # *DO NOT* leave this option enabled in production.
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
        # Client config
        api_service_name = "youtube"
        api_version = "v3"
        creds = None

        # The file youtube_token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        print('Checking local directory for existing creds...', end=" ")
        if os.path.exists('youtube_token.pickle'):
            print(Fore.GREEN + 'Creds located.' + Style.RESET_ALL)
            print('Loading youtube_token.pickle...', end=" ")
            with open('youtube_token.pickle', 'rb') as token:
                creds = pickle.load(token)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                print(Fore.MAGENTA + 'Creds expired.' + Style.RESET_ALL)
                print('Refreshing token...', end=" ")
                creds.refresh(Request())
            else:
                print(Fore.MAGENTA + 'Creds not found.' + Style.RESET_ALL)
                print('Running manual authentication...')
                time.sleep(2)
                print('You will be instructed to copy/paste a link into your browser.')
                print('You will need to follow the steps there to retrieve an auth code and paste it into the console.\n')
                time.sleep(2)
                print(Style.BRIGHT + Fore.YELLOW + 'Note: ')
                print(Style.DIM + Fore.YELLOW + 'If Google warns you that the app is not verified, you\'ll need to click on "Advanced" to find the link to proceed.' + Style.RESET_ALL)
                print(Style.BRIGHT + Fore.BLUE + 'Getting authorization URL...') 
                time.sleep(2)
                # Run auth flow
                client_secrets_file = "./youtube_client_secret.json"
                try:
                    scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
                    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                        client_secrets_file, scopes
                    )
                except:
                    print(Style.BRIGHT + Back.RED + Fore.WHITE + '\nERROR:' + Style.RESET_ALL)
                    print(Style.NORMAL + Fore.RED + 'Missing youtube_client_secret.json.' + Style.RESET_ALL)
                    print(Style.NORMAL + Fore.RED + 'Please visit the link below and follow Step 1 to obtain these credentials:' + Style.RESET_ALL)
                    print(Style.NORMAL + Fore.RED + 'https://developers.google.com/youtube/v3/quickstart/python#step_1_set_up_your_project_and_credentials' + Style.RESET_ALL)
                    print(Style.NORMAL + Fore.RED + '\nAdd them the root directory of this program in a file named youtube_client_secret.json with the following format:\n.' + Style.RESET_ALL)
                    with open("./youtube_client_secret_example.json", "r") as f:
                        example = json.load(f)
                        pprint(example)
                else:
                    try:
                        # creds = flow.run_local_server(port=1) # not working
                        creds = flow.run_console()
                    except:
                        print(Style.BRIGHT + Back.RED + Fore.WHITE + '\nERROR:' + Style.RESET_ALL)
                        print(Style.NORMAL + Fore.RED + 'Failed to authenticate. Please try again.\n' + Style.RESET_ALL)
                        # creds = flow.run_local_server(port=1) 
                        creds = flow.run_console()
                    else:
                        print(Fore.GREEN + 'Successfully authenticated!' + Style.RESET_ALL)
            # Save the credentials for the next run
            print('Creds saved to ./youtube_token.pickle for future usage.')
            with open('youtube_token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        print(Fore.GREEN + 'Creds loaded.' + Style.RESET_ALL)
        # Build and return authenticated client           
        client = googleapiclient.discovery.build(
                        api_service_name, api_version, credentials=creds
        )
        print(Fore.GREEN + 'Youtube API client successfully initialized.\n' + Style.RESET_ALL)
        self.client = client
        time.sleep(1)

    # API CALLS
    def get_all_playlists(self):
        print('Fetching your Youtube playlists...', end=" ")
        time.sleep(1)
        try:
            request = self.client.playlists().list(
                part="snippet,contentDetails",
                maxResults=25,
                mine=True
            )
            response = request.execute()
        except googleapiclient.errors.HttpError as err:
            print(Style.BRIGHT + Back.RED + Fore.WHITE + 'ERROR:' + Style.RESET_ALL)
            raise RequestError(err.resp.status, err.content.decode('utf-8'))
        else:
            print(Fore.GREEN + 'Success.\n' + Style.RESET_ALL)
            return response

    def get_playlist_items(self, id):        
        print(f'Fetching items from selected Youtube playlist...', end=" ")
        try: 
            request = self.client.playlistItems().list(
                part="snippet,contentDetails",
                maxResults=25,
                playlistId=id
            )
            response = request.execute()
        except googleapiclient.errors.HttpError as err:
            print(Style.BRIGHT + Back.RED + Fore.WHITE + 'ERROR:' + Style.RESET_ALL)
            raise RequestError(err.resp.status, err.content.decode('utf-8'))
        else:
            print(Fore.GREEN + 'Success.' + Style.RESET_ALL)
            return response

    