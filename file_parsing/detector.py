import zipfile
from pathlib import Path

import olefile

SIGNATURES: dict[str, bytes] = {
    "pdf": b"%PDF",
    "png": b"\x89PNG\r\n\x1a\n",
    "jpg": b"\xff\xd8\xff",
    "zip_based": b"PK\x03\x04",
    "ole2": b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1",
}

TEXT_EXTENSIONS = {".txt", ".md"}


def _sniff_zip_based(path: Path) -> str | None:
    try:
        with zipfile.ZipFile(path) as zf:
            names = zf.namelist()
    except zipfile.BadZipFile:
        return None
    if "word/document.xml" in names:
        return "docx"
    if "xl/workbook.xml" in names:
        return "xlsx"
    return None


def _sniff_ole2(path: Path) -> str | None:
    with olefile.OleFileIO(path) as ole:
        if ole.exists("WordDocument"):
            return "doc"
    return None


def _sniff_by_signature(path: Path) -> str | None:
    with open(path, "rb") as f:
        head = f.read(8)
    for name, sig in SIGNATURES.items():
        if head.startswith(sig):
            if name == "zip_based":
                return _sniff_zip_based(path)
            if name == "ole2":
                return _sniff_ole2(path)
            return name
    return None


def _sniff_text(path: Path) -> str | None:
    try:
        with open(path, "rb") as f:
            f.read().decode("utf-8")
        return "text"
    except UnicodeDecodeError:
        try:
            with open(path, "rb") as f:
                f.read().decode("gbk")
            return "text"
        except UnicodeDecodeError:
            return None


def detect_format(path: Path) -> str | None:
    """Signature takes precedence over extension (WeChat gives a generic
    MIME type; extensions can be spoofed)."""
    detected = _sniff_by_signature(path)
    if detected:
        return detected
    if path.suffix.lower() in TEXT_EXTENSIONS:
        return _sniff_text(path)
    return None
