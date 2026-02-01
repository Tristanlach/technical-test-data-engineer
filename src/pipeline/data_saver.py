from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Any
import os
import json
import logging

class DataSaver(ABC):
    """Abstract base class for data storage implementations."""

    @abstractmethod
    def store_dataset(self, dataset_name: str, items: List[Dict[str, Any]], run_date: str) -> str:
        """Store one dataset and return a reference (path, table name, etc.)."""
        raise NotImplementedError

    def store_all(self, data: Dict[str, List[Dict[str, Any]]], run_date: str) -> Dict[str, str]:
        """Default implementation to store all datasets."""
        return {
            name: self.store_dataset(name, items, run_date)
            for name, items in data.items()
        }

class LocalSaver(DataSaver):
    """Concrete implementation of DataSaver that saves data locally."""

    def __init__(self, storage_path: str):
        self.storage_path = Path(storage_path)
        self.logger = logging.getLogger(__name__)

    def store_dataset(self, dataset_name: str, items: List[Dict[str, Any]], run_date: str) -> str:
        """Store one dataset as a JSON file locally.

        Args:
            dataset_name (str): Name of the dataset to store.
            items (List[Dict[str, Any]]): List of dataset items to store.
            run_date (str): Run date for organizing storage.

        Returns:
            str: Path to the stored dataset file.
        """
        folder = self._dataset_path(dataset_name, run_date).parent
        folder.mkdir(parents=True, exist_ok=True)

        output_path = folder / f"{dataset_name}.json"
        tmp_path = output_path.with_suffix(".json.tmp") # Temporary file path for failure safety

        with tmp_path.open("w", encoding="utf-8") as f:
            json.dump(items, f, indent=2, ensure_ascii=False)

        os.replace(tmp_path, output_path)
        self.logger.info(f"Stored dataset {dataset_name} at {output_path}")
        return str(output_path)
    
    def load_dataset(self, dataset_name: str, run_date: str) -> List[Dict[str, Any]]:
        """Load a dataset from local storage.
        
        Args:
            dataset_name (str): Name of the dataset to load.
            run_date (str): Run date of the dataset to load.

        Returns:
            List[Dict[str, Any]]: Loaded dataset items.
        """
        input_path = self._dataset_path(dataset_name, run_date)

        if not input_path.exists():
            raise FileNotFoundError(f"No dataset found for {dataset_name} at run_date={run_date}")
        
        with input_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        self.logger.info(f"Loaded dataset {dataset_name} from {input_path}")
        return data
    
    def data_exists(self, dataset_name: str, run_date: str) -> bool:
        """Check if a dataset exists in local storage.
        
        Args:
            dataset_name (str): Name of the dataset to check.
            run_date (str): Run date of the dataset to check.
        Returns:
            bool: True if the dataset exists, False otherwise.
        """
        input_path = self._dataset_path(dataset_name, run_date)
        exists = input_path.exists()
        return exists
    
    def _dataset_path(self, dataset_name: str, run_date: str) -> Path:
        return self.storage_path / "raw" / dataset_name / f"run_date={run_date}" / f"{dataset_name}.json"