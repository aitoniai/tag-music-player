import re
from dataclasses import dataclass
from enum import StrEnum


class MediaKind(StrEnum):
    TRACK = "track"
    EPISODE = "episode"
    ALBUM = "album"
    PLAYLIST = "playlist"
    ARTIST = "artist"
    SHOW = "show"


_KINDS = "|".join(kind.value for kind in MediaKind)
_URL_PATTERN = re.compile(
    rf"^https?://open\.spotify\.com/(?:intl-[\w-]+/)?(?P<kind>{_KINDS})/(?P<id>[A-Za-z0-9]+)"
)
_URI_PATTERN = re.compile(rf"^spotify:(?P<kind>{_KINDS}):(?P<id>[A-Za-z0-9]+)$")


class InvalidSpotifyLink(ValueError):
    pass


@dataclass(frozen=True)
class SpotifyMedia:
    kind: MediaKind
    id: str

    @classmethod
    def parse(cls, link: str) -> "SpotifyMedia":
        link = link.strip()
        match = _URL_PATTERN.match(link) or _URI_PATTERN.match(link)
        if not match:
            raise InvalidSpotifyLink(f"Not a supported Spotify link: {link!r}")
        return cls(MediaKind(match["kind"]), match["id"])

    @property
    def uri(self) -> str:
        return f"spotify:{self.kind}:{self.id}"

    @property
    def is_single_item(self) -> bool:
        return self.kind in (MediaKind.TRACK, MediaKind.EPISODE)
