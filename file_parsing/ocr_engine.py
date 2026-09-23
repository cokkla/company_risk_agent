import threading

_engine = None
_lock = threading.Lock()


def get_ocr_engine():
    # ponytail: double-checked lock, 并发首次调用才会真正竞争一次，之后都是无锁读
    global _engine
    if _engine is None:
        with _lock:
            if _engine is None:
                from paddleocr import PaddleOCR

                # enable_mkldnn=False：当前 paddlepaddle/paddlex 版本下开启 oneDNN 会报
                # NotImplementedError: ConvertPirAttribute2RuntimeAttribute，已知问题
                # https://github.com/PaddlePaddle/PaddleOCR/issues/17955
                _engine = PaddleOCR(use_textline_orientation=True, lang="ch", enable_mkldnn=False)
    return _engine


def ocr_image(path) -> str:
    engine = get_ocr_engine()
    result = engine.predict(str(path))
    lines = []
    for res in result:
        lines.extend(res.get("rec_texts", []))
    return "\n".join(lines)
