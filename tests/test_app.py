from unittest.mock import Mock

from tag_music_player.app import TagMusicPlayer
from tag_music_player.media import MediaKind, SpotifyMedia
from tag_music_player.player import PlaybackError
from tag_music_player.sources import StaticSource


def test_plays_each_link_from_source():
    player = Mock()
    source = StaticSource("spotify:track:abc", "https://open.spotify.com/playlist/xyz")

    TagMusicPlayer(source, player).run()

    assert [c.args[0] for c in player.play.call_args_list] == [
        SpotifyMedia(MediaKind.TRACK, "abc"),
        SpotifyMedia(MediaKind.PLAYLIST, "xyz"),
    ]


def test_invalid_link_is_skipped():
    player = Mock()

    TagMusicPlayer(StaticSource("not a link", "spotify:track:abc"), player).run()

    player.play.assert_called_once_with(SpotifyMedia(MediaKind.TRACK, "abc"))


def test_playback_error_does_not_stop_the_loop():
    player = Mock()
    player.play.side_effect = [PlaybackError("device offline"), None]

    TagMusicPlayer(StaticSource("spotify:track:a", "spotify:track:b"), player).run()

    assert player.play.call_count == 2
