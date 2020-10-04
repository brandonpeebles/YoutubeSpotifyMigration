from tests.test_SpotifyCredentials import TestSpotifyCredentials
from tests.test_YoutubeToSpotify import TestYoutubeToSpotify
import unittest
from colorama import Fore, Back, Style


def main():
    # LOAD TESTS
    tc_SpotifyCredentials = unittest.TestLoader(
    ).loadTestsFromTestCase(TestSpotifyCredentials)
    tc_YoutubeToSpotify = unittest.TestLoader(
    ).loadTestsFromTestCase(TestYoutubeToSpotify)

    # BUILD TEST SUITES
    credentials = unittest.TestSuite(tc_SpotifyCredentials)
    youtube_migrator = unittest.TestSuite(tc_YoutubeToSpotify)

    # RUN TESTS
    runner = unittest.TextTestRunner(verbosity=2)

    print(Style.BRIGHT + Fore.YELLOW +
          "\nRUNNING UNIT TESTS..." + Style.RESET_ALL)

    print_section_header("TESTING SPOTIFY CREDENTIALS", "YELLOW")
    runner.run(credentials)

    print_section_header("TESTING YOUTUBE TO SPOTIFY MIGRATOR", "YELLOW")
    runner.run(youtube_migrator)


# helpers
def print_section_header(title, color):
    divider = "=" * 70
    if color == "YELLOW":
        color = Fore.YELLOW
    elif color == "GREEN":
        color = Fore.GREEN

    print(Style.DIM + color + f"\n{divider}" + Style.RESET_ALL)
    print(Style.BRIGHT + color + title + Style.RESET_ALL)
    print(Style.DIM + color + f"{divider}\n" + Style.RESET_ALL)


if __name__ == "__main__":
    try:
        main()
    except Exception as err:
        print(Fore.RED + err + Style.RESET_ALL)
    else:
        success_msg = (Style.BRIGHT + "SUCCESS: " +
                       Style.NORMAL + "All tests passing" + Style.RESET_ALL)
        print_section_header(success_msg, "GREEN")
