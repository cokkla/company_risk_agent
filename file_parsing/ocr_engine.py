_engine = None


def get_ocr_engine():
    global _engine
    if _engine is None:
        from paddleocr import PaddleOCR

        _engine = PaddleOCR(use_textline_orientation=True, lang="ch")
    return _engine


def ocr_image(path) -> str:
    engine = get_ocr_engine()
    result = engine.predict(str(path))
    lines = []
    for res in result:
        lines.extend(res.get("rec_texts", []))
    return "\n".join(lines)
