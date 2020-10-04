from src.migrations.YoutubeToSpotify import Migrator
import unittest
import json
import time
import requests


class TestYoutubeToSpotify(unittest.TestCase):
    """Test Migrator for YouTube to Spotify direction"""
    @classmethod
    def setUpClass(self):
        # print("\nTEST MIGRATOR FOR YOUTUBE TO SPOTIFY DIRECTION:")
        self.migrator = Migrator.__new__(Migrator)
        self.migrator._songs = []

    @classmethod
    def tearDownClass(self):
        pass
    
    def test_migrator_instance(self):
        self.assertIsInstance(self.migrator, Migrator)

if __name__ == "__main__":
    unittest.main()
