import argparse
import logging

from tag_music_player.app import TagMusicPlayer
from tag_music_player.config import Settings
from tag_music_player.player import SpotifyPlayer
from tag_music_player.sources import StaticSource

DEFAULT_LINK = "https://open.spotify.com/track/11dFghVXANMlKmJXsNCbNl"


def main() -> None:
    parser = argparse.ArgumentParser(description="Play Spotify links on this device.")
    parser.add_argument("link", nargs="?", default=DEFAULT_LINK, help="Spotify URL or URI to play")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

    settings = Settings.from_env()
    app = TagMusicPlayer(StaticSource(args.link), SpotifyPlayer.from_settings(settings))
    app.run()


if __name__ == "__main__":
    main()
