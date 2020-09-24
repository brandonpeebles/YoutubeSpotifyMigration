import src.migrations.clients.Youtube as Youtube
import src.migrations.clients.Spotify as Spotify
from pprint import pprint
from PyInquirer import prompt, Separator
from examples import custom_style_2
import sys, json
from colorama import Fore, Back, Style

class Migrator:
    """Migration methods for Youtube -> Spotify"""
    def __init__(self):
        # initialize and authenticate Youtube client instances
        self.YoutubeAPI = Youtube.Client()
        self.YoutubeAPI.authenticate()
        # initialize and authenticate Spotify client instances
        self.SpotifyAPI = Spotify.Client()
        self.SpotifyAPI.authenticate()
        # self._youtube_playlist = None
        self._songs = []

    def execute(self):
        youtube_playlist = self._get_playlist_from_input()
        if self._get_spotify_matches(youtube_playlist['items']) is False:
            print(Style.BRIGHT + Back.RED + Fore.WHITE + 'ERROR:' + Style.RESET_ALL)
            print(Style.NORMAL + Fore.RED + 'No matches found. Terminating...' + Style.RESET_ALL)
            sys.exit()
        self._confirm_spotify_matches()
    
    def _get_playlist_from_input(self):
        """
        Fetch Youtube playlists for user.
        Ask them to choose one for transferring.
        """
        playlists = self.YoutubeAPI.get_all_playlists()                         # fetch the user's playlists
        question = [                                                            # prompt user to select one
            {
                'type': 'list',
                'name': 'selectedPlaylist',
                'message': "Which Youtube playlist would you like to transfer to Spotify?",
                'choices': [{'value': idx, 'name': item["snippet"]["title"]} 
                    for idx, item in enumerate(playlists["items"])]
            }
        ]
        answer = prompt(question, style=custom_style_2)
        selectedIndex = answer['selectedPlaylist']
        selectedPlaylistId = playlists['items'][selectedIndex]['id']
        return self.YoutubeAPI.get_playlist_items(selectedPlaylistId)           # return all vids for selected playlist
        
    def _get_spotify_matches(self, items):
        """
        Fetch list of spotify search results for given array of Youtube videos.
        Youtube_dl track parsing broken after Youtube site update
        Instead, manually parse the video title. Most follow a similar format:
        {Artist name} - {Track name} {(Optional Parenthetical Statement that gets ignored here)}
        """
        print('Matching Youtube videos to Spotify songs.')
        # iterate through youtube playlist and search spotify for match
        no_matches_found = True # will remain true if none are found
        for item in items:
            title = item['snippet']['title']
            print(f"Searching Spotify for: {title}")
            try:
                # try to parse (likely) artist and track name from title
                artist, track = title.split('-')
                artist = artist.strip()
                track = track.strip()
                # remove parenthetical substr e.g. (Official Music Video)
                parenth_index = track.find('(')
                if parenth_index == -1:
                    parenth_index = len(track)
                track = track[:parenth_index]
            except:
                artist = 'Unknown'
                track = title
            # construct new song
            song = {
                # from youtube
                "youtube_title": title,
                "youtube_track": track,
                "youtube_artist": artist,
                # from querying spotify search API
                "spotify_match": self.SpotifyAPI.get_search_result(track, artist)
            }
            if song['spotify_match'] is not None:
                print(Fore.GREEN + "Match found." + Style.RESET_ALL)
                no_matches_found = False
            else:
                print(Fore.RED + "No match found." + Style.RESET_ALL)
            self._songs.append(song)
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
                                else str(idx + 1) + ': ' + song['youtube_title'] + ' (No match found)'),
                        'checked': True if song['spotify_match'] is not None else False,
                        'disabled': False if song['spotify_match'] is not None else True
                    } for idx, song in enumerate(self._songs)
                ],
                'validate': lambda answer: 'You must choose at least one song to transfer.' \
                    if len(answer) == 0 else True
            }
        ]
        answers = prompt(questions, style=custom_style_2)
        pprint(answers)

    def _transfer_songs(self):
        pass

