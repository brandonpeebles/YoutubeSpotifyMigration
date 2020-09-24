# YoutubeSpotifyMigration (WIP)
> _Transfer your playlists between Youtube and Spotify_  

User-friendly command line interface written in Python for migrating playlists between Youtube and Spotify (currently only supports Youtube -> Spotify). Makes use of OAuth 2.0 authentication to connect the program to both Google and Spotify's respective APIs and stores the refresh_tokens locally so logging in should only need to be done once. Once authenticated, it can then make API calls to fetch the user's current playlist and match songs across platforms.  

## Table of Contents  
- [Overview](#overview)
  * [Walkthrough](#walkthrough)
- [Installation](#installation)
- [Authentication Setup](#authentication-setup)
  * [Youtube](#youtube)
  * [Spotify](#spotify)
- [Usage](#usage)
- [Built with](#built-with)
- [Author](#author)

## Overview  

<p align="center">
  <img src="https://github.com/peeblesbrandon/YoutubeSpotifyMigration/blob/master/img/welcome_and_auth.png" width="500" />
</p>   
 
### Walkthrough
1. **Choose a transfer direction:** Upon initializing, `YoutubeSpotifyMigration` will ask whether you want to transfer playlists from Youtube to Spotify or the other way around. 
2. **Authentication:** It will then attempt to automatically log you in (if has your credentials stored from a previous run)  

<p align="center">
  <img src="https://github.com/peeblesbrandon/YoutubeSpotifyMigration/blob/master/img/authentication.gif" width="500" />
</p>   
 
3. **Select playlist to transfer:** You will be prompted to select a playlist to transfer songs from.  
4. **Automatic song matching:** The app will then attempt to match these songs against the other service's library using their APIs. It will flag any it couldn't find a match for. The app parses the Youtube title and first tries to search for songs in the format _Artist - Track_ and will attempt the reverse if no matches are found. 

<p align="center">
  <img src="https://github.com/peeblesbrandon/YoutubeSpotifyMigration/blob/master/img/song_matching.gif" width="500" />
</p>   
 
5. **Confirm song matches:** You will then be prompted to confirm the songs to transfer. All are selected by default. It may have made a mistake matching, so this is your chance to remove those before continuing. Press space to add/remove a song; press enter to continue.  

<p align="center">
  <img src="https://github.com/peeblesbrandon/YoutubeSpotifyMigration/blob/master/img/match_confirmation.gif" width="500" />
</p>   
 
6. **Add to new or existing playlist:** You'll then be asked whether you want to add to an existing playlist or create a new one. If adding, you'll be presented with a list of your playlists. If creating a new playlist, you'll be prompted to provide a name.   
 
<p align="center">
  <img src="https://github.com/peeblesbrandon/YoutubeSpotifyMigration/blob/master/img/select_playlist_destination.png" width="500" />
</p>  

7. **App automatically adds songs:** The app will then add all of the chosen songs into the playlist and return a URL to it.

## Installation
In order to run the app, you'll first need to clone the repository and install the necessary dependencies.

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
The app authenticates its API clients using OAuth 2.0. On the Youtube (Google) side, this is implemented using the `google-auth-oauthlib` package ([docs](http://google-auth-oauthlib.readthedocs.io)). On the Spotify side, this has been implemented through a custom built set of classes (`Spotify.py` and `SpotifyCredentials.py`) which performs their [Authorization Code Flow](https://developer.spotify.com/documentation/general/guides/authorization-guide/#authorization-code-flow). With either platform, once we've successfully authenticated and received tokens, we pickle these and store them locally to easily authenticate in the future or refresh with new tokens. 

To get started, you'll need to obtain the varous API keys, client IDs, secrets, etc. required for both platforms in order to connect to their APIs.  
  
### Youtube
You will need to obtain two main pieces of information, an API key and a client secrets JSON file. To get both of these, follow all of the instructions for *Step 1* on Google's documentation [here](https://developers.google.com/youtube/v3/quickstart/python#step_1_set_up_your_project_and_credentials). You can name your project YoutubeSpotifyMigration or anything you'd like really. The application type `Other` might not be available as the instructions say, so just choose `installed` instead.  

Once you have all of that information, you can create a file called `youtube_client_secret.json` in the root directory of your program. It should have **exactly** the following format (you can also reference the [`youtube_client_secret_example.json`](https://github.com/peeblesbrandon/YoutubeSpotifyMigration/blob/master/youtube_client_secret_example.json) file as a template too):  
```
{
  "installed": {
    "client_id": "your_client_id",
    "project_id": "your_project_id",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "your_client_secret",
    "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"],
    "YOUR_API_KEY": "your_api_key_that_you_add_yourself_to_this_json_file"
  }
}
```
  
### Spotify
You will need a similar file for Spotify.  
```
{
    "client_id": "your_client_id",
    "client_secret": "your_client_secret",
    "response_type": "code",
    "redirect_uri": "https://example.com/callback",
    "scope": "user-read-private user-read-email playlist-read-collaborative playlist-modify-public playlist-read-private playlist-modify-private"
}
```  
1. Create a file called `spotify_client_secret.json` file in the root directory of your program. Copy and paste the template in the code block above.  
1. Login into the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/).   
1. Click _Create an app_ and give it a name (e.g. YoutubeSpotifyMigration)  
1. Click _show client secret_ and copy and paste the client ID and secret into your `spotify_client_secret.json` file in their respective fields.  
1. Click _edit settings_ and enter `https://example.com/callback` into the _Redirect URIs_ input field. Click _add_ and then click _save_ to close the window.

## Usage  
1. To start the app, `cd` into the root directory of the program using your terminal and execute the `run.py` file using `python run.py`.
1. If it's your first time using the app (and you have the necessary client secrets json files added), then you should be prompted or redirected to visit a link in your browser to authenticate and grant the app permission to access your data. 
1. For Youtube, once you open the link you'll likely not have a verified app so it will warn you it's unsafe. To continue, click _Advanced_ and then you'll see a link to proceed that's labeled (unsafe). It's technically your app and you're only giving yourself access to your data, so there's nothing to worry about.
1. For Spotify, the app should automatically open your browser and direct you to a Spotify authentication page. Once you login and give permission, it should redirect you to a page that says _Example Site_. Copy the URL of this site from your browser and paste it back into the terminal.  
1. Assuming the previous two steps were successful, the app will store the credentials on your local machine and use the `refresh_token`s to automatically reauthenticate in the future.  
1. At any point, **if you need to quit the program and restart, just type:** `ctrl + c`

## Built with
* Python 3
* Youtube API
* googleapiclient
* google-auth-oauthlib
* Spotify API
* OAuth 2.0
* Pickle
* Requests  
* PyInquirer

## Author
Brandon Peebles

