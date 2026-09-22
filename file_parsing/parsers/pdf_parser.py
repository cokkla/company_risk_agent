import tempfile
from pathlib import Path

import pdfplumber

from file_parsing.ocr_engine import ocr_image
from file_parsing.registry import register
from file_parsing.types import ParsedResult


def _extract_page(page) -> str | None:
    text = page.extract_text()
    if text and text.strip():
        return text
    return None  # blank/no extractable text -> caller falls back to OCR


def _ocr_page(page) -> str:
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        tmp_path = Path(tmp.name)
    try:
        page.to_image(resolution=200).save(tmp_path)
        return ocr_image(tmp_path)
    finally:
        tmp_path.unlink(missing_ok=True)


@register("pdf")
def parse_pdf(path: Path) -> ParsedResult:
    page_errors = []
    sections = []

    with pdfplumber.open(str(path)) as pdf:
        for i, page in enumerate(pdf.pages):
            text = None
            try:
                text = _extract_page(page)
                if text is None:
                    text = _ocr_page(page)
            except Exception as e:
                page_errors.append({"page": i, "error": str(e)})

            if text is not None:
                sections.append(text)
            else:
                sections.append(f"[Page {i}: 解析失败]")

    if page_errors and len(page_errors) == len(sections):
        status = "failed"
    elif page_errors:
        status = "partial_success"
    else:
        status = "success"

    return ParsedResult(
        markdown="\n\n".join(sections),
        status=status,
        parser_used="pdfplumber",
        page_errors=page_errors,
    )
