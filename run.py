from colorama import Fore, Back, Style
from pyfiglet import Figlet
from PyInquirer import prompt, Separator
from examples import custom_style_2
import time

import src.migrations.YoutubeToSpotify as YoutubeToSpotify

def main():
    # print banner
    f = Figlet(font='cybermedium')
    print(Style.BRIGHT + Fore.YELLOW + 
        f.renderText('Youtube : Spotify Migration') + Style.RESET_ALL)
    print(Style.BRIGHT + Fore.YELLOW + 'Author: ' + Style.DIM + 'Brandon Peebles\n' + Style.RESET_ALL)
    
    # let user decide in which direction to perform transfer
    user_selection = get_transfer_direction()
    print('Great! Logging you in.\n')
    time.sleep(1)
    if user_selection['transfer_direction'] == 'Youtube ⭢  Spotify':
        migrator = YoutubeToSpotify.Migrator()
        migrator.execute()
    else:
        # run SpotifyToYoutube.Migrator()
        pass

def get_transfer_direction():                     # fetch the user's playlists
    question = [                                                            # prompt user to select one
        {
            'type': 'list',
            'name': 'transfer_direction',
            'message': "In which direction would you like to transfer playlists?",
            'choices': [
                {
                    'name': "Youtube ⭢  Spotify"
                },
                {
                    'name': "Spotify ⭢  Youtube",
                    'disabled': "Not yet available"
                }
            ]
        }
    ]
    return prompt(question, style=custom_style_2)

if __name__ == '__main__':
    main()