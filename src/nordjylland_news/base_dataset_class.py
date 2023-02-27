"""Base class that builds a dataset with the TV2 Nord API"""

import logging
import os
import time
from typing import List

from omegaconf import DictConfig

from .constants import SLEEP_MEDIUM
from .utils import init_jsonl, load_jsonl, send_request


class DataSetBuilder:
    """Base class for building datasets with the TV2 Nord API"""

    def __init__(self, dataset_name: str, cfg: DictConfig) -> None:
        """Initialize DataSetBuilder (base class).

        Args:
            dataset_name (str):
                Name of dataset.
            cfg (DictConfig):
                Hydra config.

        Attributes:
            dataset_name (str):
                Name of dataset.
            cfg (DictConfig):
                Hydra config.
            logger (logging.Logger):
                Logger.
            data_path (str):
                Path to dataset.
            max_per_page (int):
                Maximum number of articles per page.
            articles_api_url (str):
                URL to articles API.
            dataset (list of dict):
                Dataset.
            seen_uuids (set of str):
                Set of seen uuids.
            current_page (int):
                Current page to scrape.
        """
        self.dataset_name = dataset_name
        self.cfg = cfg
        self.read_cfg()

        self.logger = logging.getLogger(__name__)

        # Load dataset currently stored on disk, and use it to set current_page.
        self.dataset = self.load_dataset()

        # Get all uuids in dataset
        self.seen_uuids = set(data["uuid"] for data in self.dataset)

        # Get page from which the last articles in the dataset was scraped.
        self.current_page = self.dataset[-1]["page"] if self.dataset else 1

        # Get total number of articles in the API at the time of initialization.
        self.total_articles = self.get_total_articles()

    @property
    def data_path(self) -> str:
        """Gets data path.

        Args:
            cfg (DictConfig):
                Hydra config.

        Returns:
            str:
                Data path.
        """
        dirs = self.cfg["dirs"]
        data = dirs["data"]
        raw = dirs["raw"]
        to_root = "../" * 3  # Just Hydra things
        data_path = f"{to_root}{data}/{raw}/{self.dataset_name}.jsonl"
        return data_path

    def get_total_articles(self) -> int:
        """Gets total number of articles in the API.

        Returns:
            int:
                Total number of articles.
        """
        data = send_request(self.articles_api_url)
        total_articles = data["meta"]["total"]
        return total_articles

    def build_dataset(self) -> None:
        """Builds dataset."""
        raise NotImplementedError

    def read_cfg(self) -> None:
        """Reads config.

        Args:
            cfg (DictConfig):
                Hydra config.
        """
        self.max_per_page = self.cfg["api-info"]["max_per_page"]
        self.articles_api_url = self.cfg["api-info"]["url"]

    def get_page_with_articles(self, page: int) -> List[dict]:
        """Gets page with articles data from the API.

        Args:
            page (int):
                Page number.

        Returns:
            list of dict:
                List of articles data.
        """

        url = f"{self.articles_api_url}?page[number]={page}&page[size]={self.max_per_page}"
        data = send_request(url)
        articles = data["data"]
        return articles

    def load_dataset(self) -> List[dict]:
        """Loads dataset.

        Returns:
            list of dict:
                Dataset.
        """
        if not os.path.exists(self.data_path):
            init_jsonl(self.data_path)

        dataset = load_jsonl(self.data_path)
        return dataset

    def dataset_done(self, articles: List[dict]) -> bool:
        """Checks if dataset is done.

        If the `articles` list is empty, it means that the previous page was
        the last page containing articles. In this case, all data has been scraped,
        and the script has done its job.

        Args:
            articles (list of dict):
                List of articles data.

        Returns:
            bool:
                True if dataset is done, False otherwise.
        """

        return not bool(articles)

    def sleep(self) -> None:
        """Sleep to avoid getting blocked by the API."""
        time.sleep(SLEEP_MEDIUM)

    def page_increment(self) -> None:
        """Increments current page."""
        self.current_page += 1
