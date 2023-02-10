"""Utility functions and classes to be used throughout the project."""

from typing import List

import jsonlines
from bs4 import BeautifulSoup


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
