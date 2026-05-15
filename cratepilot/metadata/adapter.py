"""Mutagen adapter abstraction scaffolding."""


class MetadataAdapter:
    def read_tags(self, path: str) -> dict:
        raise NotImplementedError

    def write_tags(self, path: str, values: dict) -> None:
        raise NotImplementedError
