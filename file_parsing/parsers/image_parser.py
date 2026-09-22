from pathlib import Path

from file_parsing.ocr_engine import ocr_image
from file_parsing.registry import register
from file_parsing.types import ParsedResult


@register("png")
@register("jpg")
def parse_image(path: Path) -> ParsedResult:
    text = ocr_image(path)
    return ParsedResult(markdown=text, status="success", parser_used="paddleocr")
