import src.migrations.clients.Youtube as Youtube
import src.migrations.clients.Spotify as Spotify
from pprint import pprint
from PyInquirer import prompt, Separator
from examples import custom_style_2
import json

class Migrator:
    """Migration methods for Youtube -> Spotify"""
    def __init__(self):
        # initialize and authenticate Youtube client instances
        self.YoutubeAPI = Youtube.Client()
        self.YoutubeAPI.authenticate()
        # initialize and authenticate Spotify client instances
        self.SpotifyAPI = Spotify.Client()
        self.SpotifyAPI.authenticate()

    def get_playlist_from_input(self):
        """Fetch Youtube playlists for user and ask them to choose one for transferring"""
        playlists = self.YoutubeAPI.get_all_playlists()                                 # fetch the user's playlists
        question = [                                                                    # prompt user to select one
            {
                'type': 'list',
                'name': 'selectedPlaylist',
                'message': 'Which Youtube playlist would you like to transfer to Spotify?',
                'choices': [{'value': idx, 'name': item["snippet"]["title"]} for idx, item in enumerate(playlists["items"])]
            }
        ]
        answer = prompt(question, style=custom_style_2)
        selectedIndex = answer['selectedPlaylist']
        selectedPlaylistId = playlists['items'][selectedIndex]['id']
        return self.YoutubeAPI.get_playlist_items(selectedPlaylistId)['items']          # return all vids for selected playlist
        
    def get_spotify_matches(self, songsList):
        """Fetch list of spotify search results for given array of Youtube videos"""
        

    def transfer_songs(self, spotifyURIs):
        pass

