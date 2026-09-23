import subprocess
from pathlib import Path

from docx import Document

from file_parsing.parsers.doc_parser import _find_soffice, parse_doc


def _fake_convert_to_docx(converted_path: Path):
    """模拟 soffice --convert-to docx：在 subprocess.run 被调用时，
    往调用方指定的 --outdir 里放一份真实的 docx。"""

    def fake_run(cmd, **kwargs):
        outdir = Path(cmd[cmd.index("--outdir") + 1])
        doc = Document()
        doc.add_paragraph("hello from doc")
        doc.save(outdir / converted_path.name)
        return subprocess.CompletedProcess(cmd, 0)

    return fake_run


def test_parse_doc_converts_via_libreoffice_and_extracts_text(tmp_path, monkeypatch):
    monkeypatch.setattr("file_parsing.parsers.doc_parser._find_soffice", lambda: "soffice")
    monkeypatch.setattr(
        "file_parsing.parsers.doc_parser.subprocess.run",
        _fake_convert_to_docx(Path("sample.docx")),
    )
    def raise_not_found():
        raise RuntimeError("pandoc not found")

    monkeypatch.setattr("file_parsing.parsers._docx_pandoc._find_pandoc", raise_not_found)

    source = tmp_path / "sample.doc"
    source.write_bytes(b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1fake ole2 body")

    result = parse_doc(source)

    assert result.status == "success"
    assert result.parser_used == "python_docx_fallback"
    assert "hello from doc" in result.markdown


def test_parse_doc_passes_converted_path_to_convert_docx_to_markdown(tmp_path, monkeypatch):
    monkeypatch.setattr("file_parsing.parsers.doc_parser._find_soffice", lambda: "soffice")
    monkeypatch.setattr(
        "file_parsing.parsers.doc_parser.subprocess.run",
        _fake_convert_to_docx(Path("sample.docx")),
    )

    captured = {}

    def fake_convert(converted_path):
        captured["path"] = converted_path
        return "fake markdown", "pandoc"

    monkeypatch.setattr("file_parsing.parsers.doc_parser.convert_docx_to_markdown", fake_convert)

    source = tmp_path / "sample.doc"
    source.write_bytes(b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1fake ole2 body")

    result = parse_doc(source)

    assert captured["path"].name == "sample.docx"
    assert result.status == "success"
    assert result.parser_used == "pandoc"
    assert result.markdown == "fake markdown"


def test_find_soffice_uses_env_var(monkeypatch):
    monkeypatch.setenv("LIBREOFFICE_PATH", r"D:\DownLoadTools\LibreOffice\program\soffice.exe")
    assert _find_soffice() == r"D:\DownLoadTools\LibreOffice\program\soffice.exe"


def test_find_soffice_raises_when_not_found(monkeypatch):
    monkeypatch.delenv("LIBREOFFICE_PATH", raising=False)
    monkeypatch.setattr("file_parsing.parsers.doc_parser.shutil.which", lambda name: None)
    try:
        _find_soffice()
        assert False, "应该抛出 RuntimeError"
    except RuntimeError:
        pass
