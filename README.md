# YoutubeSpotifyMigration
> _Transfer your playlists between Youtube and Spotify_  

User-friendly command line interface written in Python for migrating playlists between Youtube and Spotify (currently only supports Youtube -> Spotify). Makes use of OAuth2 authentication to connect the program to both Google and Spotify's respective APIs and stores the refresh_tokens locally so logging in should only need to be done once. Once authenticated, it can then make API calls to fetch the user's current playlist and match songs across platforms.

## Installation
In order to run the program, you'll first need to clone the repository and install the necessary dependencies.

**Clone the repo:**  
```
git clone https://github.com/peeblesbrandon/YoutubeSpotifyMigration.git
```  

**Install required packages (using pip):**  
```
cd YoutubeSpotifyMigration
pip install -r requirements.txt
```  

## Authentication Setup  
The program authenticates its API clients using OAuth2. On the Youtube (Google) side, this is implemented using the `google-auth-oauthlib` package ([docs](http://google-auth-oauthlib.readthedocs.io)). On the Spotify side, this has been implemented through custom built set of classes (`Spotify.py` and `SpotifyCredentials.py`) which performs their [Authorization Code Flow](https://developer.spotify.com/documentation/general/guides/authorization-guide/#authorization-code-flow). With either platform, once we've successfully authenticated and received tokens, we pickle these and store them locally to easily authenticate in the future or refresh with new tokens. 

To get started, you'll need to obtain client IDs and secrets files for both platforms in order to connect to their APIs.  
  
**Youtube (Google)**  
[insert instructions and screenshots here]  
  
**Spotify**

## Built with
* Python 3
* Youtube API
* googleapiclient
* google-auth-oauthlib
* Spotify API
* OAuth 2.0
* Pickle
* Requests

## Author
Brandon Peebles

