import jsonlines
from bs4 import BeautifulSoup


def init_jsonl(file_name: str):
    """Initializes jsonl file

    Args:
        file_name (str):
            File name to initialize
    """
    with open(file_name, "w") as _:
        pass


def append_jsonl(data: list, file_name: str):
    """Appends data to jsonl file

    Args:
        data (list):
            Data to append
    """

    with jsonlines.open(file_name, mode="a") as writer:
        for d in data:
            writer.write(d)


def load_jsonl(file_name: str):
    """Loads jsonl file

    Args:
        file_name (str):
            File name to load

    Returns:
        list:
            Data from file

    """
    data_set = []
    with jsonlines.open(file_name, mode="r") as reader:
        for obj in reader:
            data_set.append(obj)
    return data_set


def html_to_text(html: str):
    """Converts html to text

    Args:
        html (str):
            Html to convert

    Returns:
        str:
            Text from html
    """

    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(separator=" ", strip=True)
    return text
