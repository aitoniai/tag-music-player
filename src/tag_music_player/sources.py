from collections.abc import Iterator
from typing import Protocol


class LinkSource(Protocol):
    def links(self) -> Iterator[str]: ...


class StaticSource:
    def __init__(self, *links: str):
        self._links = links

    def links(self) -> Iterator[str]:
        yield from self._links
