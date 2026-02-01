import pytest
from src.pipeline.data_saver import LocalSaver


def test_local_saver_store_and_load_roundtrip(tmp_path):
    saver = LocalSaver(storage_path=str(tmp_path))
    run_date = "2026-01-30"

    items = [{"id": 1, "name": "a"}, {"id": 2, "name": "b"}]

    out_path = saver.store_dataset("tracks", items, run_date)

    assert out_path.endswith(f"raw/tracks/run_date={run_date}/tracks.json")

    loaded = saver.load_dataset("tracks", run_date)
    assert loaded == items


def test_local_saver_exists_and_missing_load(tmp_path):
    saver = LocalSaver(storage_path=str(tmp_path))
    run_date = "2026-01-30"

    assert saver.data_exists("users", run_date) is False

    with pytest.raises(FileNotFoundError):
        saver.load_dataset("users", run_date)

    saver.store_dataset("users", [{"id": 123}], run_date)
    assert saver.data_exists("users", run_date) is True