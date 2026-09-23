import json

from file_parsing import writer
from file_parsing.pipeline import parse_file
from file_parsing.source import LocalFileSource


def _safe_id(file_id: str) -> str:
    return file_id.replace("/", "_").replace("\\", "_")


def test_parse_txt_end_to_end(tmp_path):
    target = tmp_path / "sample.txt"
    target.write_text("hello world", encoding="utf-8")
    file_id = str(target)

    result = parse_file(file_id, LocalFileSource())

    assert result.status == "success"
    safe_id = _safe_id(file_id)
    assert (writer.OUTPUT_DIR / f"{safe_id}.md").exists()
    manifest = json.loads((writer.OUTPUT_DIR / f"{safe_id}_manifest.json").read_text(encoding="utf-8"))
    assert manifest["status"] == "success"
    assert manifest["detected_type"] == "text"


def test_unsupported_format_is_failed(tmp_path):
    unsupported = tmp_path / "sample.bin"
    unsupported.write_bytes(b"\x00\x01\x02\x03")
    file_id = str(unsupported)

    result = parse_file(file_id, LocalFileSource())

    assert result.status == "failed"
    assert not (writer.OUTPUT_DIR / f"{_safe_id(file_id)}.md").exists()


def test_same_stem_different_extension_do_not_collide(tmp_path):
    # 回归测试：曾用 Path(source_filename).stem 做输出文件名，
    # 导致 report.txt 与 report.docx 写到同一个 report.md，后者覆盖前者。
    from docx import Document

    txt = tmp_path / "report.txt"
    txt.write_text("from txt", encoding="utf-8")

    docx = tmp_path / "report.docx"
    Document().save(docx)

    source = LocalFileSource()
    parse_file(str(txt), source)
    parse_file(str(docx), source)

    txt_md = writer.OUTPUT_DIR / f"{_safe_id(str(txt))}.md"
    docx_md = writer.OUTPUT_DIR / f"{_safe_id(str(docx))}.md"
    assert txt_md.exists()
    assert docx_md.exists()
    assert txt_md.read_text(encoding="utf-8") == "from txt"


def test_stale_md_removed_on_failed_reparse(tmp_path):
    # 回归测试：同一 file_id 先成功解析（写出 .md），
    # 内容原地改坏后重新解析失败，旧 .md 不应残留。
    target = tmp_path / "flaky.txt"
    target.write_text("first pass ok", encoding="utf-8")
    file_id = str(target)
    safe_id = _safe_id(file_id)

    parse_file(file_id, LocalFileSource())
    assert (writer.OUTPUT_DIR / f"{safe_id}.md").exists()

    target.write_bytes(b"\xff\xfe\x00\xff")  # utf-8/gbk 均无法解码
    result = parse_file(file_id, LocalFileSource())

    assert result.status == "failed"
    assert not (writer.OUTPUT_DIR / f"{safe_id}.md").exists()


def test_file_id_with_path_separators_does_not_escape_output_dir(tmp_path):
    # file_id 目前直接就是完整路径字符串，写文件名前必须转义分隔符，
    # 否则会被当作子目录/上级目录处理。
    target = tmp_path / "nested.txt"
    target.write_text("data", encoding="utf-8")
    file_id = str(target)
    assert "/" in file_id or "\\" in file_id

    parse_file(file_id, LocalFileSource())

    for entry in writer.OUTPUT_DIR.iterdir():
        assert entry.parent == writer.OUTPUT_DIR
