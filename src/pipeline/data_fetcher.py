
import logging
import requests
from typing import Any, Dict, List
from src.pipeline.config import ENDPOINTS, PAGE_SIZE


class APIDataFetcher:
    """Fetcher class to fetch data from an API."""
    
    def __init__(self, base_url: str, page_size: int = PAGE_SIZE):
        self.base_url = base_url
        self.page_size = page_size
        self.logger = logging.getLogger(__name__)

    def fetch_page(self, endpoint: str, page: int) -> Dict[str, Any]:
        """Fetch a single page of data from the API.

        Args:
            endpoint (str): API endpoint to fetch data from.
            page (int): Page number to fetch.

        Returns:
            Dict[str, Any]: JSON response from the API.
        """
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        params = {"page": page, "size": self.page_size}
        
        try:
            self.logger.info(f"Fetching page {page} from {endpoint}")
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            self.logger.exception(f"Timeout while fetching {url}")
            raise
        except requests.exceptions.RequestException:
            self.logger.exception(f"Error fetching data from {url}")
            raise

    def fetch_all_pages(self, endpoint: str) -> List[Dict[str, Any]]:
        """Fetch all pages of data from the and API endpoint.

        Args:
            endpoint (str): API endpoint to fetch data from.

        Returns:
            List[Dict[str, Any]]: List of all items fetched from the API.
        """
        all_items = []
        page = 1
        max_pages = 10000

        while page <= max_pages:
            data = self.fetch_page(endpoint, page)
            items = data.get("items", [])
            
            if not items:
                break
            
            all_items.extend(items) # Add fetched items
            
            if page >= data.get("pages", 1):
                break
            
            page += 1

        if page > max_pages:
            raise RuntimeError(f"Pagination seems stuck for endpoint={endpoint}")
        
        self.logger.info(f"Fetched {len(all_items)} items from {endpoint}")
        return all_items
    

    def fetch_all_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """Fetch all data from all endpoints.

        Returns:
            Dict[str, List[Dict[str, Any]]]: Dictionary with endpoint names as keys and lists of items as values.
        """
        result = {}
        
        for endpoint_name, endpoint_path in ENDPOINTS.items():
            self.logger.info(f"Fetching all data from {endpoint_name}...")
            result[endpoint_name] = self.fetch_all_pages(endpoint_path)
        
        self.logger.info(f"Successfully fetched data from {len(result)} endpoints")
        return result
