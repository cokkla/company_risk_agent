from file_parsing.detector import detect_format


def test_detects_plain_text(tmp_path):
    path = tmp_path / "sample.txt"
    path.write_text("hello world", encoding="utf-8")
    assert detect_format(path) == "text"


def test_detects_gbk_text(tmp_path):
    path = tmp_path / "sample.txt"
    path.write_bytes("你好".encode("gbk"))
    assert detect_format(path) == "text"


def test_signature_overrides_wrong_extension(tmp_path):
    # 企微给的是通用 MIME、扩展名可被伪造，签名优先
    fake = tmp_path / "fake.txt"
    fake.write_bytes(b"%PDF-1.4 not a real pdf")
    assert detect_format(fake) == "pdf"


def test_detects_png_signature(tmp_path):
    path = tmp_path / "image.bin"
    path.write_bytes(b"\x89PNG\r\n\x1a\n" + b"rest of file")
    assert detect_format(path) == "png"


def test_detects_jpg_signature(tmp_path):
    path = tmp_path / "image.bin"
    path.write_bytes(b"\xff\xd8\xff" + b"rest of file")
    assert detect_format(path) == "jpg"


def test_detects_docx_via_zip_contents(tmp_path):
    import zipfile

    path = tmp_path / "sample.docx"
    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr("word/document.xml", "<xml/>")
    assert detect_format(path) == "docx"


def test_detects_xlsx_via_zip_contents(tmp_path):
    import zipfile

    path = tmp_path / "sample.xlsx"
    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr("xl/workbook.xml", "<xml/>")
    assert detect_format(path) == "xlsx"


def test_zip_without_known_markers_is_unsupported(tmp_path):
    import zipfile

    path = tmp_path / "sample.zip"
    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr("unrelated.txt", "hi")
    assert detect_format(path) is None


def test_undecodable_bytes_with_text_extension_is_unsupported(tmp_path):
    # 既不匹配任何签名，也无法按 utf-8/gbk 解码
    path = tmp_path / "broken.txt"
    path.write_bytes(b"\xff\xfe\x00\xff")
    assert detect_format(path) is None


def test_unknown_binary_without_text_extension_is_unsupported(tmp_path):
    path = tmp_path / "sample.bin"
    path.write_bytes(b"\x00\x01\x02\x03")
    assert detect_format(path) is None


def test_detects_doc_via_ole2_word_document_stream(tmp_path, monkeypatch):
    class FakeOle:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def exists(self, name):
            return name == "WordDocument"

    monkeypatch.setattr("file_parsing.detector.olefile.OleFileIO", lambda path: FakeOle())

    path = tmp_path / "sample.doc"
    path.write_bytes(b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1" + b"rest of file")
    assert detect_format(path) == "doc"


def test_ole2_without_word_document_stream_is_unsupported(tmp_path, monkeypatch):
    # .xls/.ppt 等同为 OLE2 容器但没有 WordDocument stream，不在本期支持范围
    class FakeOle:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def exists(self, name):
            return False

    monkeypatch.setattr("file_parsing.detector.olefile.OleFileIO", lambda path: FakeOle())

    path = tmp_path / "sample.xls"
    path.write_bytes(b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1" + b"rest of file")
    assert detect_format(path) is None
