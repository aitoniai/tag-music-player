import pytest

from tag_music_player.media import InvalidSpotifyLink, MediaKind, SpotifyMedia


@pytest.mark.parametrize(
    "link, kind, media_id",
    [
        ("https://open.spotify.com/track/4uLU6hMCjMI75M1A2tKUQC", MediaKind.TRACK, "4uLU6hMCjMI75M1A2tKUQC"),
        ("https://open.spotify.com/track/4uLU6hMCjMI75M1A2tKUQC?si=abc123", MediaKind.TRACK, "4uLU6hMCjMI75M1A2tKUQC"),
        ("https://open.spotify.com/intl-de/album/1DFixLWuPkv3KT3TnV35m3", MediaKind.ALBUM, "1DFixLWuPkv3KT3TnV35m3"),
        ("https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M", MediaKind.PLAYLIST, "37i9dQZF1DXcBWIGoYBM5M"),
        ("spotify:playlist:37i9dQZF1DXcBWIGoYBM5M", MediaKind.PLAYLIST, "37i9dQZF1DXcBWIGoYBM5M"),
        ("  spotify:track:4uLU6hMCjMI75M1A2tKUQC\n", MediaKind.TRACK, "4uLU6hMCjMI75M1A2tKUQC"),
    ],
)
def test_parse_valid_links(link, kind, media_id):
    media = SpotifyMedia.parse(link)

    assert media.kind is kind
    assert media.id == media_id
    assert media.uri == f"spotify:{kind}:{media_id}"


@pytest.mark.parametrize(
    "link",
    ["", "https://example.com/track/abc", "https://open.spotify.com/user/someone", "spotify:track:"],
)
def test_parse_invalid_links(link):
    with pytest.raises(InvalidSpotifyLink):
        SpotifyMedia.parse(link)


def test_single_item_kinds():
    assert SpotifyMedia(MediaKind.TRACK, "x").is_single_item
    assert SpotifyMedia(MediaKind.EPISODE, "x").is_single_item
    assert not SpotifyMedia(MediaKind.PLAYLIST, "x").is_single_item
