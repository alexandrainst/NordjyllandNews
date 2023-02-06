import os
import time

import requests

from nordjylland_news.constants import HEADERS, MAX_PER_PAGE, RAW_DATA_PATH
from nordjylland_news.utils import append_jsonl, html_to_text, init_jsonl, load_jsonl


class SummaryDataSetBuilder:
    """Builds data set with article text content and article summary"""

    def __init__(self):
        self.seen_uuids = self.get_seen_uuids()
        self.article_count = len(self.seen_uuids)

    def get_seen_uuids(self):
        """Gets seen uuids

        Returns:
            set:
                Seen uuids
        """
        if not os.path.exists(RAW_DATA_PATH):
            init_jsonl(RAW_DATA_PATH)

        articles = load_jsonl(RAW_DATA_PATH)
        return set(article["uuid"] for article in articles)

    def build_data_set(self, total_articles: int, sleep: int = 30):
        """Builds article text content to article summary data set

        Starts from page 1 if data_set is empty, otherwise continues from
        latests unfinished page.

        Args:
            total_articles (int): Total number of articless to get
            sleep (int): Number of seconds to sleep between each page
        """

        if self.article_count >= total_articles:
            print(
                f"Total articless already reached: {self.article_count}/{total_articles}"
            )
            return None

        currrent_page = self.article_count // MAX_PER_PAGE + 1

        while True:
            new_articles = []
            articles_data = self.get_page_with_articles_data(page=currrent_page)
            if not articles_data:
                print(f"{self.article_count}/{total_articles}")
                print("No more articles")
                return None
            else:
                for article_data in articles_data:
                    uuid = self.get_uuid(article_data)
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
                        if self.article_count >= total_articles:
                            print(
                                f"Total articless reached: {self.article_count}/{total_articles}"
                            )
                            append_jsonl(new_articles, RAW_DATA_PATH)
                            return None

                currrent_page += 1

            append_jsonl(new_articles, RAW_DATA_PATH)

            print(f"{self.article_count}/{total_articles}")
            time.sleep(sleep)

    @staticmethod
    def get_page_with_articles_data(page: int):
        """
        Args:
            page (int): Page number

        Returns:
            list:
                List of articles data
        """

        url = f"https://public.nord.bazo.dk/v1/articles?page[number]={page}&page[size]={MAX_PER_PAGE}"
        while True:
            try:
                response = requests.get(url, headers=HEADERS)
                if response.status_code == 429:
                    time.sleep(5)
                elif response.status_code != 200:
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
    def get_uuid(article: dict):
        uuid = article["uuid"]
        return uuid

    @staticmethod
    def get_text_content(article: dict):
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
    def get_summary(article: dict):
        summary = article["summary"]
        return summary
