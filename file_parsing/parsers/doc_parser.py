import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from file_parsing.parsers._docx_pandoc import convert_docx_to_markdown
from file_parsing.registry import register
from file_parsing.types import ParsedResult


def _find_soffice() -> str:
    configured = os.environ.get("LIBREOFFICE_PATH")
    if configured:
        return configured
    found = shutil.which("soffice")
    if found:
        return found
    raise RuntimeError(
        "找不到 LibreOffice 的 soffice 可执行文件，"
        "请设置环境变量 LIBREOFFICE_PATH 指向 soffice(.exe) 路径，或将其加入 PATH"
    )


@register("doc")
def parse_doc(path: Path) -> ParsedResult:
    soffice = _find_soffice()
    with tempfile.TemporaryDirectory() as tmpdir:
        subprocess.run(
            [soffice, "--headless", "--convert-to", "docx", "--outdir", tmpdir, str(path)],
            check=True,
            capture_output=True,
        )
        converted = Path(tmpdir) / f"{path.stem}.docx"
        markdown, parser_used = convert_docx_to_markdown(converted)
    return ParsedResult(markdown=markdown, status="success", parser_used=parser_used)
