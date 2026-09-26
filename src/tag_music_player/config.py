import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    device_name: str
    token_cache_path: Path

    @classmethod
    def from_env(cls) -> "Settings":
        load_dotenv()
        return cls(
            device_name=os.getenv("SPOTIFY_DEVICE_NAME", "tag-music-player"),
            token_cache_path=Path(os.getenv("SPOTIFY_TOKEN_CACHE", ".cache-spotify")),
        )
