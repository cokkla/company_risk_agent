from pathlib import Path

from file_parsing import parsers  # noqa: F401  (import triggers @register side effects)
from file_parsing.detector import detect_format
from file_parsing.registry import PARSERS
from file_parsing.source import FileSource
from file_parsing.types import ParsedResult
from file_parsing.writer import write_output


def parse_file(file_id: str, source: FileSource) -> ParsedResult:
    path = source.get_path(file_id)
    detected_type = detect_format(path)

    if detected_type is None or detected_type not in PARSERS:
        result = ParsedResult(markdown="", status="failed", parser_used="none",
                               warnings=[f"unsupported format: {detected_type}"])
    else:
        result = PARSERS[detected_type](path)

    write_output(path.name, detected_type, result)
    return result
