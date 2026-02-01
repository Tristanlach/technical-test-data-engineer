from src.pipeline.data_fetcher import APIDataFetcher
import pytest
from src.pipeline.config import ENDPOINTS

def test_fetch_all_pages_aggregates_and_stops(monkeypatch):
    fetcher = APIDataFetcher(base_url="http://fake", page_size=100)

    calls = []

    def fake_fetch_page(endpoint, page):
        calls.append((endpoint, page))
        if page == 1:
            return {"items": [{"id": 1}, {"id": 2}], "pages": 2}
        if page == 2:
            return {"items": [{"id": 3}], "pages": 2}
        return {"items": [], "pages": 2}

    monkeypatch.setattr(fetcher, "fetch_page", fake_fetch_page)

    items = fetcher.fetch_all_pages("/tracks")

    assert items == [{"id": 1}, {"id": 2}, {"id": 3}]
    assert calls == [("/tracks", 1), ("/tracks", 2)]


def test_fetch_all_pages_raises_if_pagination_stuck(monkeypatch):
    fetcher = APIDataFetcher(base_url="http://fake", page_size=100)

    def fake_fetch_page(endpoint, page):
        return {"items": [{"id": page}], "pages": 999999999}

    monkeypatch.setattr(fetcher, "fetch_page", fake_fetch_page)

    with pytest.raises(RuntimeError, match="Pagination seems stuck"):
        fetcher.fetch_all_pages("/tracks")


def test_fetch_all_data_returns_all_datasets(monkeypatch):
    fetcher = APIDataFetcher(base_url="http://fake", page_size=100)

    def fake_fetch_all_pages(endpoint):
        return [{"endpoint": endpoint}]

    monkeypatch.setattr(fetcher, "fetch_all_pages", fake_fetch_all_pages)

    out = fetcher.fetch_all_data()

    assert set(out.keys()) == set(ENDPOINTS.keys())
    assert out["tracks"] == [{"endpoint": ENDPOINTS["tracks"]}]
    assert out["users"] == [{"endpoint": ENDPOINTS["users"]}]
    assert out["listen_history"] == [{"endpoint": ENDPOINTS["listen_history"]}]
