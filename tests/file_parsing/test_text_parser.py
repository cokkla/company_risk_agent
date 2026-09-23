from file_parsing.parsers.text_parser import parse_text


def test_parse_text_utf8(tmp_path):
    path = tmp_path / "sample.txt"
    path.write_text("hello world", encoding="utf-8")

    result = parse_text(path)

    assert result.status == "success"
    assert result.markdown == "hello world"
    assert result.parser_used == "text_direct"


def test_parse_text_gbk_fallback(tmp_path):
    path = tmp_path / "sample.txt"
    path.write_bytes("你好世界".encode("gbk"))

    result = parse_text(path)

    assert result.status == "success"
    assert result.markdown == "你好世界"
