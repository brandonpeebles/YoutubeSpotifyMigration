import unittest
import json
import os
import time
import requests
os.chdir("..")
from src.migrations.YoutubeToSpotify import Migrator


class TestYoutubeToSpotify(unittest.TestCase):
    """Test Migrator for YouTube to Spotify direction"""
    @classmethod
    def setUpClass(self):
        print("\nTEST MIGRATOR FOR YOUTUBE TO SPOTIFY DIRECTION:")
        self.migrator = Migrator.__new__(Migrator)
        self.migrator._songs = []

    def test_migrator_instance(self):
        self.assertIsInstance(self.migrator, Migrator)

if __name__ == "__main__":
    unittest.main()
