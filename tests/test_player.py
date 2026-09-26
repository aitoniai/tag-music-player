from unittest.mock import Mock

import pytest
from spotipy import SpotifyException

from tag_music_player.media import MediaKind, SpotifyMedia
from tag_music_player.player import DeviceNotFound, PlaybackError, SpotifyPlayer


@pytest.fixture
def client():
    client = Mock()
    client.devices.return_value = {
        "devices": [{"id": "phone-id", "name": "Phone"}, {"id": "pi-id", "name": "Tag-Music-Player"}]
    }
    return client


def test_plays_track_as_uri_list(client):
    SpotifyPlayer(client, "tag-music-player").play(SpotifyMedia(MediaKind.TRACK, "abc"))

    client.start_playback.assert_called_once_with(device_id="pi-id", uris=["spotify:track:abc"])


def test_plays_playlist_as_context(client):
    SpotifyPlayer(client, "tag-music-player").play(SpotifyMedia(MediaKind.PLAYLIST, "xyz"))

    client.start_playback.assert_called_once_with(device_id="pi-id", context_uri="spotify:playlist:xyz")


def test_missing_device_raises(client):
    with pytest.raises(DeviceNotFound, match="Phone"):
        SpotifyPlayer(client, "kitchen").play(SpotifyMedia(MediaKind.TRACK, "abc"))

    client.start_playback.assert_not_called()


def test_api_error_raises_playback_error(client):
    client.start_playback.side_effect = SpotifyException(403, -1, "Premium required")

    with pytest.raises(PlaybackError, match="Premium required"):
        SpotifyPlayer(client, "tag-music-player").play(SpotifyMedia(MediaKind.TRACK, "abc"))
