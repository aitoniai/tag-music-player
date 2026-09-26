import logging
from typing import Protocol

import spotipy
from spotipy.oauth2 import SpotifyOAuth

from tag_music_player.config import Settings
from tag_music_player.media import SpotifyMedia

log = logging.getLogger(__name__)


class Player(Protocol):
    def play(self, media: SpotifyMedia) -> None: ...


class PlaybackError(RuntimeError):
    pass


class DeviceNotFound(PlaybackError):
    pass


class SpotifyPlayer:
    SCOPES = "user-read-playback-state user-modify-playback-state"

    def __init__(self, client: spotipy.Spotify, device_name: str):
        self._client = client
        self._device_name = device_name

    @classmethod
    def from_settings(cls, settings: Settings) -> "SpotifyPlayer":
        auth = SpotifyOAuth(
            scope=cls.SCOPES,
            cache_handler=spotipy.CacheFileHandler(cache_path=str(settings.token_cache_path)),
            open_browser=False,
        )
        return cls(spotipy.Spotify(auth_manager=auth), settings.device_name)

    def play(self, media: SpotifyMedia) -> None:
        device_id = self._find_device_id()
        log.info("Playing %s on %s", media.uri, self._device_name)
        try:
            if media.is_single_item:
                self._client.start_playback(device_id=device_id, uris=[media.uri])
            else:
                self._client.start_playback(device_id=device_id, context_uri=media.uri)
        except spotipy.SpotifyException as error:
            raise PlaybackError(f"Spotify refused to play {media.uri}: {error.msg}") from error

    def _find_device_id(self) -> str:
        devices = self._client.devices()["devices"]
        for device in devices:
            if device["name"].casefold() == self._device_name.casefold():
                return device["id"]
        available = ", ".join(d["name"] for d in devices) or "none"
        raise DeviceNotFound(f"Spotify device {self._device_name!r} not found (available: {available})")
