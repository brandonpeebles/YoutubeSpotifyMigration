from src.migrations.YoutubeToSpotify import Migrator
import src.migrations.clients.Youtube as Youtube
import src.migrations.clients.Spotify as Spotify
import unittest
import PyInquirer
from unittest.mock import patch
import json
import time
import requests


class TestYoutubeToSpotify(unittest.TestCase):
    """Test Migrator for YouTube to Spotify direction"""
    @classmethod
    def setUpClass(self):
        # print("\nTEST MIGRATOR FOR YOUTUBE TO SPOTIFY DIRECTION:")
        self.migrator = Migrator.__new__(Migrator)
        self.migrator.YoutubeAPI = Youtube.Client()
        self.migrator._songs = []

    @classmethod
    def tearDownClass(self):
        pass

    def test_migrator_instance(self):
        self.assertIsInstance(self.migrator, Migrator)

    @patch('src.migrations.clients.Youtube.Client.get_all_playlists')
    @patch('src.migrations.clients.Youtube.Client.get_playlist_items')
    @patch('src.migrations.YoutubeToSpotify.prompt')
    def test_get_playlist_from_input(self, mock_prompt, mock_get_playlist_items, mock_get_all_playlists):
        mock_get_all_playlists.return_value = {
            'items': [
                {
                    'id': 123,
                    'snippet': {'title': 'test playlist title from all playlists'}
                }
            ]
        }
        mock_get_playlist_items.return_value = {
            'title': 'test playlist title from items'
        }
        mock_prompt.return_value = {'selectedPlaylist': 0}
        self.assertEqual(self.migrator._get_playlist_from_input(), {
                         'title': 'test playlist title from all playlists'})


if __name__ == "__main__":
    unittest.main()
