from unittest.mock import Mock

import pytest
import requests
from spotipy import SpotifyException
from spotipy.oauth2 import SpotifyOauthError

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


def test_device_lookup_error_raises_playback_error(client):
    client.devices.side_effect = SpotifyException(503, -1, "Service unavailable")

    with pytest.raises(PlaybackError, match="Service unavailable"):
        SpotifyPlayer(client, "tag-music-player").play(SpotifyMedia(MediaKind.TRACK, "abc"))


def test_auth_error_raises_playback_error(client):
    client.devices.side_effect = SpotifyOauthError("invalid_grant")

    with pytest.raises(PlaybackError, match="invalid_grant"):
        SpotifyPlayer(client, "tag-music-player").play(SpotifyMedia(MediaKind.TRACK, "abc"))


def test_network_error_raises_playback_error(client):
    client.start_playback.side_effect = requests.ConnectionError("network down")

    with pytest.raises(PlaybackError, match="network down"):
        SpotifyPlayer(client, "tag-music-player").play(SpotifyMedia(MediaKind.TRACK, "abc"))


def test_restricted_device_without_id_raises(client):
    client.devices.return_value = {"devices": [{"id": None, "name": "tag-music-player"}]}

    with pytest.raises(PlaybackError, match="restricted"):
        SpotifyPlayer(client, "tag-music-player").play(SpotifyMedia(MediaKind.TRACK, "abc"))

    client.start_playback.assert_not_called()
