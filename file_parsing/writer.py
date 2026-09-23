import json
from datetime import datetime, timezone
from pathlib import Path

from file_parsing.types import ParsedResult

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "parsed_output"


def write_output(file_id: str, source_filename: str, detected_type: str | None, result: ParsedResult) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    safe_id = file_id.replace("/", "_").replace("\\", "_")  # file_id 可能是路径字符串，去掉分隔符防止跨目录写
    md_path = OUTPUT_DIR / f"{safe_id}.md"

    if result.status != "failed":
        md_path.write_text(result.markdown, encoding="utf-8")
    else:
        md_path.unlink(missing_ok=True)  # 清理上一次成功解析留下的陈旧 .md

    manifest = {
        "source_filename": source_filename,
        "detected_type": detected_type,
        "parser_used": result.parser_used,
        "status": result.status,
        "warnings": result.warnings,
        "page_errors": result.page_errors,
        "parsed_at": datetime.now(timezone.utc).isoformat(),
    }
    (OUTPUT_DIR / f"{safe_id}_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
