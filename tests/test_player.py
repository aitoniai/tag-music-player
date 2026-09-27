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
    client.shuffle.assert_called_once_with(False, device_id="pi-id")
    client.repeat.assert_called_once_with("off", device_id="pi-id")


def test_plays_playlist_as_context(client):
    SpotifyPlayer(client, "tag-music-player").play(SpotifyMedia(MediaKind.PLAYLIST, "xyz"))

    client.start_playback.assert_called_once_with(
        device_id="pi-id", context_uri="spotify:playlist:xyz", offset={"position": 0}
    )
    client.shuffle.assert_called_once_with(False, device_id="pi-id")
    client.repeat.assert_called_once_with("off", device_id="pi-id")


def test_plays_album_from_first_track(client):
    SpotifyPlayer(client, "tag-music-player").play(SpotifyMedia(MediaKind.ALBUM, "alb"))

    client.start_playback.assert_called_once_with(
        device_id="pi-id", context_uri="spotify:album:alb", offset={"position": 0}
    )


def test_plays_artist_without_offset(client):
    SpotifyPlayer(client, "tag-music-player").play(SpotifyMedia(MediaKind.ARTIST, "art"))

    client.start_playback.assert_called_once_with(device_id="pi-id", context_uri="spotify:artist:art")


def test_shuffle_repeat_error_does_not_fail_playback(client, caplog):
    client.repeat.side_effect = SpotifyException(502, -1, "Bad gateway")

    SpotifyPlayer(client, "tag-music-player").play(SpotifyMedia(MediaKind.TRACK, "abc"))

    client.start_playback.assert_called_once()
    assert "Bad gateway" in caplog.text


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
