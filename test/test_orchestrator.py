from src.pipeline.orchestrator import Orchestrator


class DummyFetcher:
    def fetch_all_data(self):
        return {
            "tracks": [{"id": 1}, {"id": 2}],
            "users": [{"id": 10}],
        }

class DummySaver:
    def __init__(self):
        self.called_with = None

    def store_all(self, data, run_date):
        self.called_with = (data, run_date)
        return {
            "tracks": f"/fake/path/tracks/{run_date}.json",
            "users": f"/fake/path/users/{run_date}.json",
        }

def test_orchestrator_returns_counts_and_outputs():
    fetcher = DummyFetcher()
    saver = DummySaver()
    orch = Orchestrator(fetcher=fetcher, saver=saver)

    out = orch.run_pipeline(run_date="2026-01-30")

    assert out["counts"] == {"tracks": 2, "users": 1}
    assert out["outputs"]["tracks"].endswith("2026-01-30.json")
    assert saver.called_with[1] == "2026-01-30"