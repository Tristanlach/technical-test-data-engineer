import logging
from src.pipeline.orchestrator import Orchestrator
from src.pipeline.data_fetcher import APIDataFetcher
from src.pipeline.data_saver import LocalSaver
from src.pipeline.config import API_BASE_URL, DATA_DIR


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger(__name__)
    logger.info("Starting orchestrator execution.")

    fetcher = APIDataFetcher(API_BASE_URL)
    saver = LocalSaver(DATA_DIR)
    orchestrator = Orchestrator(fetcher, saver)

    try:
        orchestrator.run_pipeline()
        logger.info("Orchestrator execution completed.")
    except Exception as e:
        logger.error(f"Orchestrator execution failed: {e}")


if __name__ == "__main__":
    main()
