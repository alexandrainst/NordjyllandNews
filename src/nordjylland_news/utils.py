"""Utility functions and classes to be used throughout the project."""

import logging
import time
from typing import List

import jsonlines
import requests
from bs4 import BeautifulSoup

from .constants import (
    ERROR_500,
    HEADERS,
    SLEEP_LONG,
    SLEEP_SHORT,
    STATUS_CODE_OK,
    TOO_MANY_REQUESTS,
)

logger = logging.getLogger(__name__)


def init_jsonl(file_name: str) -> None:
    """Initializes jsonl file.

    The function is used in the DataSetBuilder class to initialize
    the dataset file, if it does not already exist.

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
    dataset = []
    with jsonlines.open(file_name, mode="r") as reader:
        for obj in reader:
            dataset.append(obj)
    return dataset


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


def send_request(url: str) -> dict:
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
                time.sleep(SLEEP_SHORT)
            elif response.status_code == ERROR_500:
                time.sleep(SLEEP_LONG)
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
