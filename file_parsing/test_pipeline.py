import json
import shutil
from pathlib import Path

from file_parsing.detector import detect_format
from file_parsing.pipeline import parse_file
from file_parsing.source import LocalFileSource
from file_parsing.writer import OUTPUT_DIR

FIXTURES = Path(__file__).parent / "test_fixtures"


def test_detect_format_text():
    assert detect_format(FIXTURES / "sample.txt") == "text"


def test_detect_format_wrong_extension_follows_signature():
    # a .txt-named file with a PDF signature must be detected as pdf, not text
    fake = FIXTURES / "fake.txt"
    fake.write_bytes(b"%PDF-1.4 not a real pdf")
    try:
        assert detect_format(fake) == "pdf"
    finally:
        fake.unlink()


def test_parse_txt_end_to_end():
    shutil.rmtree(OUTPUT_DIR, ignore_errors=True)
    result = parse_file(str(FIXTURES / "sample.txt"), LocalFileSource())
    assert result.status == "success"
    assert (OUTPUT_DIR / "sample.md").exists()
    manifest = json.loads((OUTPUT_DIR / "sample_manifest.json").read_text(encoding="utf-8"))
    assert manifest["status"] == "success"
    assert manifest["detected_type"] == "text"


def test_unsupported_format_is_failed():
    shutil.rmtree(OUTPUT_DIR, ignore_errors=True)
    unsupported = FIXTURES / "sample.bin"
    unsupported.write_bytes(b"\x00\x01\x02\x03")
    try:
        result = parse_file(str(unsupported), LocalFileSource())
        assert result.status == "failed"
        assert not (OUTPUT_DIR / "sample.md").exists()
    finally:
        unsupported.unlink()


if __name__ == "__main__":
    FIXTURES.mkdir(exist_ok=True)
    (FIXTURES / "sample.txt").write_text("hello world", encoding="utf-8")

    test_detect_format_text()
    test_detect_format_wrong_extension_follows_signature()
    test_parse_txt_end_to_end()
    test_unsupported_format_is_failed()
    print("all checks passed")
