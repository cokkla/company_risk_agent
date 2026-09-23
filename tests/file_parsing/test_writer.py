import json

from file_parsing import writer
from file_parsing.types import ParsedResult
from file_parsing.writer import write_output


def test_write_output_success_writes_markdown_and_manifest():
    result = ParsedResult(markdown="# hi", status="success", parser_used="text_direct")

    write_output("file-1", "source.txt", "text", result)

    assert (writer.OUTPUT_DIR / "file-1.md").read_text(encoding="utf-8") == "# hi"
    manifest = json.loads((writer.OUTPUT_DIR / "file-1_manifest.json").read_text(encoding="utf-8"))
    assert manifest["source_filename"] == "source.txt"
    assert manifest["detected_type"] == "text"
    assert manifest["parser_used"] == "text_direct"
    assert manifest["status"] == "success"


def test_write_output_failed_does_not_write_markdown():
    result = ParsedResult(markdown="", status="failed", parser_used="none", warnings=["boom"])

    write_output("file-2", "source.bin", None, result)

    assert not (writer.OUTPUT_DIR / "file-2.md").exists()
    manifest = json.loads((writer.OUTPUT_DIR / "file-2_manifest.json").read_text(encoding="utf-8"))
    assert manifest["status"] == "failed"
    assert manifest["warnings"] == ["boom"]


def test_write_output_failed_removes_previous_markdown():
    ok = ParsedResult(markdown="old content", status="success", parser_used="text_direct")
    write_output("file-3", "source.txt", "text", ok)
    assert (writer.OUTPUT_DIR / "file-3.md").exists()

    failed = ParsedResult(markdown="", status="failed", parser_used="none")
    write_output("file-3", "source.txt", "text", failed)

    assert not (writer.OUTPUT_DIR / "file-3.md").exists()


def test_write_output_sanitizes_path_separators_in_file_id():
    result = ParsedResult(markdown="data", status="success", parser_used="text_direct")

    write_output("a/b\\c", "source.txt", "text", result)

    assert (writer.OUTPUT_DIR / "a_b_c.md").exists()
    assert not (writer.OUTPUT_DIR / "a").exists()
