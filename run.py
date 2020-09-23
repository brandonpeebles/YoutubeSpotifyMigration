import src.migrations.YoutubeToSpotify as YoutubeToSpotify

if __name__ == '__main__':
    migrator = YoutubeToSpotify.Migrator()
    selectedPlaylist = migrator.get_playlist_from_input()
    # spotifyMatches = 