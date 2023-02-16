"""Class that builds and contains the summarisation dataset."""

import os
import time
from typing import List, Set

import requests

from .constants import (
    HEADERS,
    MAX_PER_PAGE,
    RAW_DATA_PATH,
    SLEEP_5_SECONDS,
    STATUS_CODE_OK,
    TOO_MANY_REQUESTS,
)
from .utils import append_jsonl, html_to_text, init_jsonl, load_jsonl


class SummaryDataSetBuilder:
    """Builds data set with article text content and article summary."""

    def __init__(self):
        self.seen_uuids = self.get_seen_uuids()
        self.article_count = len(self.seen_uuids)

    def get_seen_uuids(self) -> Set[str]:
        """Gets seen uuids.

        Every article has a uuid. This method gets all uuids
        from the current data set, and is used to avoid duplicates.

        Returns:
            set:
                Seen uuids.
        """
        if not os.path.exists(RAW_DATA_PATH):
            init_jsonl(RAW_DATA_PATH)

        articles = load_jsonl(RAW_DATA_PATH)
        return set(article["uuid"] for article in articles)

    def build_data_set(self, total_articles: int, sleep: int = 30) -> None:
        """Builds article text content to article summary data set.

        Starts from page 1 if data_set is empty, otherwise continues from
        latests unfinished page. When total_articles is reached, or there are
        no more articles, the method stops and returns None.

        Args:
            total_articles (int):
                Total number of articless to get.
            sleep (int, optional):
                Number of seconds to sleep between each page. Defaults to 30.
        """

        # If total_articles already is reached, stop and return None
        if self.article_count >= total_articles:
            print(
                f"Total articless already reached: {self.article_count}/{total_articles}"
            )
            return None

        # Get current page
        currrent_page = self.article_count // MAX_PER_PAGE + 1

        # Iterate over pages until total_articles is reached or until a page with no articles is visited.
        while True:
            new_articles = []
            articles_data = self.get_page_with_articles_data(page=currrent_page)

            # Check if there are no more articles to process.
            # If the `articles_data` list is empty, it means that the previous page was
            # the last page containing articles. In this case, stop processing and return None.
            if not articles_data:
                print(f"{self.article_count}/{total_articles}")
                print("No more articles")
                return None
            else:
                # Iterate over articles on current page
                for article_data in articles_data:
                    uuid = self.get_uuid(article_data)

                    # If article uuid is not seen, add it to seen uuids and process article.
                    if uuid not in self.seen_uuids:
                        self.seen_uuids.add(uuid)
                        text_content = self.get_text_content(article_data)
                        summary = self.get_summary(article_data)
                        articles = {
                            "uuid": uuid,
                            "text_content": text_content,
                            "summary": summary,
                        }
                        new_articles.append(articles)

                        self.article_count += 1

                        # Check if total_articles is reached.
                        # If so, stop processing, append new articles to data set and return None.
                        if self.article_count >= total_articles:
                            print(
                                f"Total articless reached: {self.article_count}/{total_articles}"
                            )
                            append_jsonl(new_articles, RAW_DATA_PATH)
                            return None

                # Go to next page.
                currrent_page += 1

            # Append new articles to data set.
            append_jsonl(new_articles, RAW_DATA_PATH)

            print(f"{self.article_count}/{total_articles}")
            time.sleep(sleep)

    @staticmethod
    def get_page_with_articles_data(page: int) -> List[dict]:
        """
        Args:
            page (int):
                Page number.

        Returns:
            list of dict:
                List of articles data.
        """

        url = f"https://public.nord.bazo.dk/v1/articles?page[number]={page}&page[size]={MAX_PER_PAGE}"
        while True:
            try:
                response = requests.get(url, headers=HEADERS)
                if response.status_code == TOO_MANY_REQUESTS:
                    time.sleep(SLEEP_5_SECONDS)
                elif response.status_code != STATUS_CODE_OK:
                    raise Exception(
                        f"Request failed for url: {url} with status code: {response.status_code}"
                    )
                else:
                    data = response.json()
                    break
            except requests.RequestException:
                print("Request failed for url: ", url)

        articles_data = data["data"]
        return articles_data

    @staticmethod
    def get_uuid(article: dict) -> str:
        """Gets uuid from article.

        Args:
            article (dict):
                Article data.

        Returns:
            str:
                Article uuid.
        """
        uuid = article["uuid"]
        return uuid

    @staticmethod
    def get_text_content(article: dict) -> str:
        """Gets text content from article.

        Args:
            article (dict):
                Article data.

        Returns:
            str:
                Article text content.
        """
        text_bits = []
        all_content = article["content"]
        for content in all_content:
            if content["type"] == "Text":
                html = content["content"]["html"]
                text = html_to_text(html)
                text_bits.append(text)
        text = " ".join(text_bits)
        return text.strip()

    @staticmethod
    def get_summary(article: dict) -> str:
        """Gets summary from article.

        Args:
            article (dict):
                Article data.

        Returns:
            str:
                Article summary.
        """
        summary = article["summary"]
        return summary
