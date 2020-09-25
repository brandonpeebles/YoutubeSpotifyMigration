import src.migrations.clients.Youtube as Youtube
import src.migrations.clients.Spotify as Spotify
from pprint import pprint
from PyInquirer import prompt, Separator
from examples import custom_style_2
import sys, json, time
from colorama import Fore, Back, Style

class Migrator:
    """Migration class for Spotify -> Youtub"""
    def __init__(self):
        # initialize and authenticate Youtube client instances
        self.YoutubeAPI = Youtube.Client()
        self.YoutubeAPI.authenticate()
        # initialize and authenticate Spotify client instances
        self.SpotifyAPI = Spotify.Client()
        self.SpotifyAPI.authenticate()
        # self._youtube_playlist = None
        self._songs = []

    # MAIN
    def execute(self):
        spotify_playlist = self._get_playlist_from_input()
        if self._get_youtube_matches(spotify_playlist['items']) is False:
            print(Style.BRIGHT + Back.RED + Fore.WHITE + 'ERROR:' + Style.RESET_ALL)
            print(Style.NORMAL + Fore.RED + 'No matches found. Terminating...' + Style.RESET_ALL)
            sys.exit()
        # uri_list = self._confirm_spotify_matches()
        # self._transfer_songs(uri_list, youtube_playlist['title'])
    
    # HELPER METHODS
    def _get_playlist_from_input(self):
        """
        Fetch Spotify playlists for user.
        Ask user to choose one for transferring.
        """
        playlists = self.SpotifyAPI.get_all_playlists()                         # fetch the user's playlists
        question = [                                                            # prompt user to select one
            {
                'type': 'list',
                'name': 'selectedPlaylist',
                'message': "Which Spotify playlist would you like to transfer to Youtube?",
                'choices': [{'value': idx, 'name': item["name"]} 
                    for idx, item in enumerate(playlists)]
            }
        ]
        answer = prompt(question, style=custom_style_2)
        selectedIndex = answer['selectedPlaylist']
        selectedPlaylistId = playlists[selectedIndex]['id']
        selectedPlaylistTitle = playlists[selectedIndex]['name']
        playlist_items = self.SpotifyAPI.get_playlist_items(selectedPlaylistId)
        playlist_items = {
            'name': selectedPlaylistTitle,
            'items': playlist_items
        }                                                                       # add playlist title onto the obj
        return playlist_items
        
    def _get_youtube_matches(self, items):
        """
        Fetch list of YouTube search results for given array of Spotify songs
        Searches for videos using the following query format:
        {Artist name} - {Track name} 
        """
        print('Matching Spotify songs to Spotify videos.')
        # iterate through playlist and search YouTube for match
        no_matches_found = True # will remain true if none are found
        for item in items:
            track = item['track']['name']
            artist = item['track']['artists'][0]['name']
            print(f"Searching YouTube for: {artist} - {track}")
            # concat track and artist to create search string
            song_str = artist + " - " + track
            # construct new song
            song = {
                # from spotify
                "spotify_track": track,
                "spotify_artist": artist,
                # from querying spotify search API
                "youtube_match": self.YoutubeAPI.get_search_result(song_str)
            }
            if song['youtube_match'] is not None:
                print(Fore.GREEN + "Match found." + Style.RESET_ALL)
                no_matches_found = False
            else:
                print(Fore.RED + "No match found." + Style.RESET_ALL)
            self._songs.append(song)
        print()
        return no_matches_found == False

    def _confirm_spotify_matches(self):
        """
        Prompt user with checkbox list of matches from search results
        Ask them to confirm the list before proceeding to transfer to Spotify
        They may uncheck any box to skip over during transfer
        If no match found, checkbox should be disabled
        """
        questions = [
            {
                'type': 'checkbox',
                'message': 'Confirm songs for transfer. Uncheck to skip.',
                'name': 'transfer_list',
                'choices': [
                    {
                        # 'value': idx, causes bug where 'checked' is ignored -- will parse index out of name
                        'name': (str(idx + 1) + ': ' + song['spotify_match']['artists'][0]['name'] + ' - ' + song['spotify_match']['name'] 
                                if song['spotify_match'] 
                                else str(idx + 1) + ': ' + song['youtube_title']),
                        'checked': True if song['spotify_match'] is not None else False,
                        'disabled': False if song['spotify_match'] is not None else "No match found"
                    } for idx, song in enumerate(self._songs)
                ],
                'validate': lambda answer: 'You must choose at least one song to transfer.' \
                    if len(answer) == 0 else True
            }
        ]
        answers = prompt(questions, style=custom_style_2)
        # filter our songs list for just the ones selected by the user
        selected_indices = []
        for song in answers['transfer_list']:
            colon_idx = song.find(':')
            original_idx = int(song[0:colon_idx]) - 1
            selected_indices.append(original_idx)
        return [self._songs[i]['spotify_match']['uri'] for i in selected_indices]
        
    def _transfer_songs(self, song_list, youtube_playlist_title):
        question = [                                                            # prompt user to select one
            {
                'type': 'list',
                'name': 'transfer_method',
                'message': "Would you like to create a new playlist or add to an existing one?",
                'choices': [
                    {
                        'name': "Create new playlist"
                    },
                    {
                        'name': "Add to existing playlist"
                    }
                ]
            }
        ]
        answer = prompt(question, style=custom_style_2)['transfer_method']
        if answer == 'Create new playlist':
            question = [
                {
                    'type': 'input',
                    'name': 'new_playlist_name',
                    'message': 'Enter a name for your new playlist:',
                    'default': youtube_playlist_title,
                    'validate': lambda answer: 'You must enter a name for your playlist.' \
                    if len(answer) == 0 else True
                }
            ]
            new_playlist_name = prompt(question, style=custom_style_2)['new_playlist_name']
            playlist_id = self.SpotifyAPI.create_playlist(song_list, new_playlist_name)            
        else:
            # get spotify playlists
            user_playlists = self.SpotifyAPI.get_all_playlists()
            # prompt for selection and
            # filter out playlists that the user can\'t modify
            user_id = self.SpotifyAPI.get_user_id()
            question = [                                                            # prompt user to select one
                {
                    'type': 'list',
                    'name': 'selectedPlaylist',
                    'message': "Which playlist would you like to transfer the songs to?",
                    'choices': [
                        {
                            'value': idx, 
                            'name': playlist["name"]
                            # 'disabled': False if (playlist['owner']['id'] == user_id or playlist['collaborative'] == True) 
                            #     else "Unable to modify this playlist" 
                        } for idx, playlist in enumerate(user_playlists) 
                            if (playlist['owner']['id'] == user_id 
                                or playlist['collaborative'] == True)]
                }
            ]
            answer = prompt(question, style=custom_style_2)
            selectedIndex = answer['selectedPlaylist']
            # get the playlist_id
            playlist_id = user_playlists[selectedIndex]['id']
        # add to songs to new or selected playlist and print out the URL
        playlist_URL = self.SpotifyAPI.add_songs_to_playlist(song_list, playlist_id)
        print(Fore.YELLOW + f"\nDone! Playlist available at:", end=" ")
        print(Fore.BLUE + playlist_URL + Style.RESET_ALL + "\n")