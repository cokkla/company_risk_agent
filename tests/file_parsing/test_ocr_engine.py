import threading

import pytest

from file_parsing import ocr_engine


@pytest.fixture(autouse=True)
def reset_singleton():
    ocr_engine._engine = None
    yield
    ocr_engine._engine = None


def test_get_ocr_engine_returns_singleton(monkeypatch):
    created = []

    class FakePaddleOCR:
        def __init__(self, **kwargs):
            created.append(kwargs)

    monkeypatch.setattr("paddleocr.PaddleOCR", FakePaddleOCR)

    first = ocr_engine.get_ocr_engine()
    second = ocr_engine.get_ocr_engine()

    assert first is second
    assert len(created) == 1


def test_get_ocr_engine_is_constructed_once_under_concurrent_first_calls(monkeypatch):
    # 回归测试：修复前的懒加载单例没有锁，多个线程同时首次调用会各自构造一份引擎。
    created = []
    creation_started = threading.Event()
    release_creation = threading.Event()

    class SlowFakePaddleOCR:
        def __init__(self, **kwargs):
            creation_started.set()
            release_creation.wait(timeout=2)
            created.append(kwargs)

    monkeypatch.setattr("paddleocr.PaddleOCR", SlowFakePaddleOCR)

    results = []

    def call():
        results.append(ocr_engine.get_ocr_engine())

    t1 = threading.Thread(target=call)
    t2 = threading.Thread(target=call)

    t1.start()
    creation_started.wait(timeout=2)
    t2.start()  # 此时第一个线程仍在构造中，第二个线程应被锁挡住而不是再构造一份
    release_creation.set()

    t1.join(timeout=2)
    t2.join(timeout=2)

    assert len(created) == 1
    assert results[0] is results[1]
