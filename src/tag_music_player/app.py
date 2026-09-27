import logging

from tag_music_player.media import InvalidSpotifyLink, SpotifyMedia
from tag_music_player.player import PlaybackError, Player
from tag_music_player.sources import LinkSource

log = logging.getLogger(__name__)


class TagMusicPlayer:
    def __init__(self, source: LinkSource, player: Player):
        self._source = source
        self._player = player

    def run(self) -> None:
        for link in self._source.links():
            self.handle(link)

    def handle(self, link: str) -> None:
        try:
            self._player.play(SpotifyMedia.parse(link))
        except (InvalidSpotifyLink, PlaybackError) as error:
            log.error("%s", error)
