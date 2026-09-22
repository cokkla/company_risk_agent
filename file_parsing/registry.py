from collections.abc import Callable
from pathlib import Path

from file_parsing.types import ParsedResult

PARSERS: dict[str, Callable[[Path], ParsedResult]] = {}


def register(type_name: str):
    def decorator(fn: Callable[[Path], ParsedResult]):
        PARSERS[type_name] = fn
        return fn

    return decorator
