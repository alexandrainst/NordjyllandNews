"""Base class that builds a dataset with the TV2 Nord API"""

import logging
import os
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List

import requests
from omegaconf import DictConfig

from .constants import ERROR_500, HEADERS, STATUS_CODE_OK, TOO_MANY_REQUESTS
from .utils import init_jsonl, load_jsonl


class DataSetBuilder(ABC):
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
            sleep_length (dict of int):
                Length of sleep in seconds.
        """
        self.dataset_name = dataset_name
        self.logger = logging.getLogger(self.dataset_name)

        self.read_cfg(cfg)

        # Load dataset currently stored on disk, and use it to set current_page.
        self.dataset = self.load_dataset() if not self.testing else []

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
        if self.dataset_name == "test":
            data_path = f"{self.dataset_name}.jsonl"
        else:
            dirs = self.cfg["dirs"]
            data = dirs["data"]
            raw = dirs["raw"]
            data_path = Path(data) / raw / f"{self.dataset_name}.jsonl"
        return data_path

    def get_total_articles(self) -> int:
        """Gets total number of articles in the API.

        Returns:
            total_articles (int):
                Total number of articles.
        """
        data = self.send_request(self.articles_api_url)
        total_articles = data["meta"]["total"]
        return total_articles

    @abstractmethod
    def build_dataset(self) -> None:
        """Builds dataset."""
        pass

    def read_cfg(self, cfg) -> None:
        """Reads config.

        Args:
            cfg (DictConfig):
                Hydra config.
        """
        self.max_per_page = cfg["api_info"]["max_per_page"]
        self.articles_api_url = cfg["api_info"]["url"]
        self.sleep_length = {
            "short": cfg["sleeps"]["short"],
            "medium": cfg["sleeps"]["medium"],
            "long": cfg["sleeps"]["long"],
        }
        self.testing = cfg["testing"]
        self.cfg = cfg

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
        data = self.send_request(url)
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
        time.sleep(self.sleep_length["medium"])

    def page_increment(self) -> None:
        """Increments current page."""
        self.current_page += 1

    def send_request(self, url: str) -> dict:
        """Sends request.

        Args:
            url (str):
                Url to send request to.
            headers (dict):
                Headers to send with request.

        Returns:
            dict:
                Response data.
        """
        while True:
            try:
                response = requests.get(url, headers=HEADERS)
                if response.status_code == TOO_MANY_REQUESTS:
                    time.sleep(self.sleep_length["short"])
                elif response.status_code == ERROR_500:
                    time.sleep(self.sleep_length["long"])
                elif response.status_code != STATUS_CODE_OK:
                    raise Exception(
                        f"Request failed for url: {url} with status code: {response.status_code}"
                    )
                else:
                    data = response.json()
                    break
            except requests.RequestException:
                self.logger.info(f"Request failed for url: {url}")
        return data
