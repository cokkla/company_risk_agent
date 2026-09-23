from pathlib import Path

from file_parsing.parsers._docx_pandoc import convert_docx_to_markdown
from file_parsing.registry import register
from file_parsing.types import ParsedResult


@register("docx")
def parse_docx(path: Path) -> ParsedResult:
    markdown, parser_used = convert_docx_to_markdown(path)
    return ParsedResult(markdown=markdown, status="success", parser_used=parser_used)
