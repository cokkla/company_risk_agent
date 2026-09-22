from pathlib import Path

from file_parsing.registry import register
from file_parsing.types import ParsedResult


@register("text")
def parse_text(path: Path) -> ParsedResult:
    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        content = path.read_text(encoding="gbk")
    return ParsedResult(markdown=content, status="success", parser_used="text_direct")
