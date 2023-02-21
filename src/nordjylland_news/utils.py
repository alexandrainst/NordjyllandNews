"""Utility functions and classes to be used throughout the project."""

import logging
import time
from typing import List

import jsonlines
import requests
from bs4 import BeautifulSoup

from .constants import (
    ARTICLES_API_URL,
    ERROR_500,
    HEADERS,
    MAX_PER_PAGE,
    SLEEP_5_SECONDS,
    SLEEP_15_MINUTES,
    STATUS_CODE_OK,
    TOO_MANY_REQUESTS,
)

logger = logging.getLogger(__name__)


def init_jsonl(file_name: str) -> None:
    """Initializes jsonl file.

    The function is used in the SummaryDataSetBuilder class to initialize
    the data set file, if it does not already exist.

    Args:
        file_name (str):
            File name to initialize.
    """
    with open(file_name, "w") as _:
        pass


def append_jsonl(data: list, file_name: str) -> None:
    """Appends data to jsonl file.

    Args:
        data (list):
            Data to append.
        file_name (str):
            The name of the JSONL file where the data should be appended.
    """

    with jsonlines.open(file_name, mode="a") as writer:
        for d in data:
            writer.write(d)


def load_jsonl(file_name: str) -> List[dict]:
    """Loads jsonl file.

    Args:
        file_name (str):
            File name to load.

    Returns:
        list of dict:
            Data from file.

    """
    data_set = []
    with jsonlines.open(file_name, mode="r") as reader:
        for obj in reader:
            data_set.append(obj)
    return data_set


def html_to_text(html: str) -> str:
    """Converts html to text.

    Args:
        html (str):
            Html to convert.

    Returns:
        str:
            Text from html.
    """

    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(separator=" ", strip=True)
    return text


def send_request(url) -> dict:
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
                time.sleep(SLEEP_5_SECONDS)
            elif response.status_code == ERROR_500:
                time.sleep(SLEEP_15_MINUTES)
            elif response.status_code != STATUS_CODE_OK:
                raise Exception(
                    f"Request failed for url: {url} with status code: {response.status_code}"
                )
            else:
                data = response.json()
                break
        except requests.RequestException:
            logger.info(f"Request failed for url: {url}")
    return data


def get_total_articles() -> int:
    """Gets total number of articles.

    Returns:
        int:
            Total number of articles.
    """
    data = send_request(ARTICLES_API_URL)
    total_articles = data["meta"]["total"]
    return total_articles


def get_page_with_articles_data(page: int) -> List[dict]:
    """Gets page with articles data from the API.

    Args:
        page (int):
            Page number.

    Returns:
        list of dict:
            List of articles data.
    """

    url = f"{ARTICLES_API_URL}?page[number]={page}&page[size]={MAX_PER_PAGE}"
    data = send_request(url)
    articles_data = data["data"]
    return articles_data
