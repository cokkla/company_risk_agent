from pathlib import Path

import openpyxl

from file_parsing.registry import register
from file_parsing.types import ParsedResult


@register("xlsx")
def parse_xlsx(path: Path) -> ParsedResult:
    wb = openpyxl.load_workbook(str(path), data_only=True)
    sections = []
    for sheet in wb.worksheets:
        lines = [f"## {sheet.title}"]
        for row in sheet.iter_rows(values_only=True):
            lines.append(" | ".join("" if v is None else str(v).replace("|", "\\|") for v in row))
        sections.append("\n".join(lines))
    return ParsedResult(markdown="\n\n".join(sections), status="success", parser_used="openpyxl")
