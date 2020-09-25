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
                    scopes = ["https://www.googleapis.com/auth/youtube.readonly", "https://www.googleapis.com/auth/youtube.force-ssl"]
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
        """get all playlists for authenticated user"""
        # print('Fetching your Youtube playlists...', end=" ")
        print('\nFetching your Youtube playlists...', end=" ")
        time.sleep(1)
        try:
            request = self.client.playlists().list(
                part="snippet,contentDetails",
                maxResults=50,
                mine=True
            )
            response = request.execute()
            nextPageToken = response.get('nextPageToken', None)
            while nextPageToken is not None:
                time.sleep(1)
                request = self.client.playlists().list(
                    part="snippet,contentDetails",
                    maxResults=50,
                    playlistId=id,
                    pageToken=nextPageToken
                )
                nextResponse = request.execute()
                response['items'].extend(nextResponse['items'])
                nextPageToken = nextResponse.get('nextPageToken', None)
        except googleapiclient.errors.HttpError as err:
            print(Style.BRIGHT + Back.RED + Fore.WHITE + 'ERROR:' + Style.RESET_ALL)
            raise RequestError(err.resp.status, err.content.decode('utf-8'))
        else:
            print(Fore.GREEN + 'Success.\n' + Style.RESET_ALL)
            return response

    def get_playlist_items(self, id):    
        """get full details of videos for a given playlist id"""    
        print(f'\nFetching items from selected Youtube playlist...', end=" ")
        try: 
            request = self.client.playlistItems().list(
                part="snippet,contentDetails",
                maxResults=50,
                playlistId=id
            )
            response = request.execute()
            nextPageToken = response.get('nextPageToken', None)
            while nextPageToken is not None:
                time.sleep(1)
                request = self.client.playlistItems().list(
                    part="snippet,contentDetails",
                    maxResults=50,
                    playlistId=id,
                    pageToken=nextPageToken
                )
                nextResponse = request.execute()
                response['items'].extend(nextResponse['items'])
                nextPageToken = nextResponse.get('nextPageToken', None)
        except googleapiclient.errors.HttpError as err:
            print(Style.BRIGHT + Back.RED + Fore.WHITE + 'ERROR' + Style.RESET_ALL)
            raise RequestError(err.resp.status, err.content.decode('utf-8'))
        else:
            print(Fore.GREEN + 'Success.\n' + Style.RESET_ALL)
            return response

    def get_search_result(self, query_str):
        """
        Get first youtube search result for given query string.
        Return first video object or None
        """
        try:
            request = self.client.search().list(
                part="snippet",
                type="video",
                maxResults=1,
                q=query_str
            )
            response = request.execute()
        except googleapiclient.errors.HttpError as err:
            print(Style.BRIGHT + Back.RED + Fore.WHITE + 'ERROR' + Style.RESET_ALL)
            raise RequestError(err.resp.status, err.content.decode('utf-8'))
        else:
            if len(response['items']) == 0:
                return None                                                     # no results
            else:
                return response['items'][0]                                     # return first video
    
    def create_playlist(self, playlist_name):
        """
        Creates a new empty playlist and returns its playlist_id
        Defaults privacy status to public
        """
        try:
            request = self.client.playlists().insert(
            part="snippet,status",
            body={
            "snippet": {
                    "title": playlist_name,
                    "description": "Created via YouTubeSpotifyMigration.",
                    "tags": [
                        "YouTubeSpotifyMigration",
                        "API call",
                        "music"
                    ],
                    "defaultLanguage": "en"
                },
                "status": {
                    "privacyStatus": "public"
                }
                }
            )
            response = request.execute()
        except googleapiclient.errors.HttpError as err:
            print(Style.BRIGHT + Back.RED + Fore.WHITE + 'ERROR' + Style.RESET_ALL)
            raise RequestError(err.resp.status, err.content.decode('utf-8'))
        else:
            return response['id']

    def add_videos_to_playlist(self, video_list, playlist_id):
        """
        Add videos iteratively to playlist by its id
        Return URL to playlist
        """
        try:
            for video in video_list:
                request = self.client.playlistItems().insert(
                    part="snippet",
                    body={
                    "snippet": {
                        "playlistId": playlist_id,
                        "resourceId": {
                            "kind": video['id']['kind'],
                            "videoId": video['id']['videoId']
                        }
                    }
                    }
                )
                request.execute()
                time.sleep(0.2)                                                   # wait 1 sec to not exceed youtube quota
        except googleapiclient.errors.HttpError as err:
            print(Style.BRIGHT + Back.RED + Fore.WHITE + 'ERROR' + Style.RESET_ALL)
            raise RequestError(err.resp.status, err.content.decode('utf-8'))
        return f"https://www.youtube.com/playlist?list={playlist_id}"