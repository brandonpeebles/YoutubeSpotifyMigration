from colorama import Fore, Back, Style
from pyfiglet import Figlet

import src.migrations.YoutubeToSpotify as YoutubeToSpotify

if __name__ == '__main__':
    f = Figlet(font='cybermedium')
    print(Style.BRIGHT + Fore.YELLOW + 
        f.renderText('Youtube : Spotify Migration') + Style.RESET_ALL)
    migrator = YoutubeToSpotify.Migrator()
    migrator.execute()
    # spotifyMatches = 