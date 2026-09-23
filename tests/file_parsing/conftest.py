import pytest

from file_parsing import writer


@pytest.fixture(autouse=True)
def isolated_output_dir(tmp_path, monkeypatch):
    """每个测试用独立的输出目录，避免相互污染、也不再写到项目根目录下。"""
    output_dir = tmp_path / "parsed_output"
    monkeypatch.setattr(writer, "OUTPUT_DIR", output_dir)
    return output_dir
