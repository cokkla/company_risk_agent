from pathlib import Path
from typing import Protocol


class FileSource(Protocol):
    def get_path(self, file_id: str) -> Path:
        """Return a local filesystem path for the given file id."""
        ...


class LocalFileSource:
    """Stand-in for D2's file-query interface (file_id -> binary stream).
    Treats file_id as an already-local path until that interface exists."""

    def get_path(self, file_id: str) -> Path:
        return Path(file_id)
