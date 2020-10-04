import unittest
import json, os, time
import requests
os.chdir("..")
from src.migrations.clients.credentials.SpotifyCredentials import Credentials

class TestSpotifyCredentials(unittest.TestCase):
    """TEST SPOTIFY CREDENTIALS:"""
    @classmethod
    def setUpClass(self):
        print("\nTEST SPOTIFY CREDENTIALS:")
        creds_json = json.loads(
        """
            {
                "access_token": "access_token_value",
                "token_type": "Bearer",
                "expires_in": 3600,
                "refresh_token": "refresh_token_value",
                "scope": "playlist-read-private playlist-read-collaborative playlist-modify-private playlist-modify-public user-read-email user-read-private"
            }
        """
        )
        self.creds = Credentials(creds_json, "auth_header_value")
    
    def test_getters(self):
        self.assertEqual(self.creds.access_token(), "access_token_value")
        self.assertEqual(self.creds.refresh_token(), "refresh_token_value")
        self.assertEqual(self.creds.auth_header(), "auth_header_value")

    def test_expiry(self):
        self.assertFalse(self.creds.expired(), "new creds should not be expired")
        old_expiry = self.creds._expiry 
        self.creds._set_expiry(2)
        self.assertNotEqual(old_expiry, self.creds._expiry, "expiry should have updated")
        time.sleep(3) # so creds expire
        self.assertTrue(self.creds.expired(), "creds should have expired")
        self.creds._set_expiry(3600)

    def test_validity(self):
        self.assertTrue(self.creds.valid())
        # add test for refresh method 

if __name__ == "__main__":
    unittest.main() 
