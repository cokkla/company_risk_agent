import json
from datetime import datetime, timezone
from pathlib import Path

from file_parsing.types import ParsedResult

OUTPUT_DIR = Path("./parsed_output")


def write_output(source_filename: str, detected_type: str | None, result: ParsedResult) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    stem = Path(source_filename).stem

    if result.status != "failed":
        (OUTPUT_DIR / f"{stem}.md").write_text(result.markdown, encoding="utf-8")

    manifest = {
        "source_filename": source_filename,
        "detected_type": detected_type,
        "parser_used": result.parser_used,
        "status": result.status,
        "warnings": result.warnings,
        "page_errors": result.page_errors,
        "parsed_at": datetime.now(timezone.utc).isoformat(),
    }
    (OUTPUT_DIR / f"{stem}_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
