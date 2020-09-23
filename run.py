import src.migrations.YoutubeToSpotify as YoutubeToSpotify

if __name__ == '__main__':
    migrator = YoutubeToSpotify.Migrator()
    migrator.execute()
    # spotifyMatches = 