import logging
from datetime import date
from typing import Any, Dict, Optional
from src.pipeline.data_fetcher import APIDataFetcher
from src.pipeline.data_saver import DataSaver

class Orchestrator:
    
    def __init__(self, fetcher: APIDataFetcher, saver: DataSaver):
        self.fetcher = fetcher
        self.saver = saver
        self.logger = logging.getLogger(__name__)

    def run_pipeline(self, run_date: Optional[str] = None) -> Dict[str, Any]:
        """Run the data fetching and storage pipeline.

        Args:
            run_date (Optional[str]): Date string to tag the run. Defaults to today's date.

        Returns:
            Dict[str, Any]: References to stored datasets.
        """  
        run_date = run_date or date.today().isoformat()
        self.logger.info(f"Starting pipeline run_date={run_date}")

        try:
            data = self.fetcher.fetch_all_data()
        except Exception as e:
            self.logger.error(f"Data fetching failed: {e}")
            raise

        try:
            outputs = self.saver.store_all(data, run_date)
        except Exception as e:
            self.logger.error(f"Data saving failed: {e}")
            raise

        counts = {name: len(items) for name, items in data.items()}

        self.logger.info(f"Pipeline finished successfully")
        self.logger.info(f"Counts: {counts}")
        self.logger.info(f"Outputs: {outputs}")

        return {"counts": counts, "outputs": outputs}
