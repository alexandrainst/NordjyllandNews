"""Class that builds and contains the summarisation dataset."""


from typing import Dict, List

from omegaconf import DictConfig

from .base_dataset_class import DataSetBuilder
from .utils import append_jsonl, html_to_text


class SummaryDataSetBuilder(DataSetBuilder):
    """Builds dataset with article text content and article summary."""

    def __init__(self, dataset_name: str, cfg: DictConfig) -> None:
        super().__init__(dataset_name=dataset_name, cfg=cfg)

        # Number of articles in dataset
        self.dataset_length = len(self.seen_uuids)

    def build_dataset(self) -> None:
        """Builds article text content to article summary dataset.
        Starts from page self.current_page. When a page is reached that has no articles,
        the method stops and returns None.

        """
        self.logger.info("Building summarisation dataset")

        # Iterate over pages until a page with no articles is visited.
        while True:
            new_data: List[Dict] = []
            articles = self.get_page_with_articles(page=self.current_page)

            if self.dataset_done(articles):
                self.logger.info("Dataset done.")
                return
            else:
                # Iterate over articles on current page
                for article in articles:
                    uuid = article["uuid"]

                    # If article uuid is not seen, add it to seen uuids and process article.
                    if uuid not in self.seen_uuids:
                        self.seen_uuids.add(uuid)
                        self.dataset_length += 1

                        data = self.get_article_data(article)
                        new_data.append(data)

            # Append new data to dataset.
            append_jsonl(new_data, self.data_path)

            # Log progress
            self.logger.info(f"{self.dataset_length}/{self.total_articles}")

            self.page_increment()
            self.sleep()

    def get_article_data(self, article: dict) -> Dict:
        """Gets article text content and summary.

        Args:
            article (dict):
                Article data.

        Returns:
            data (dict):
                Article text content and summary + meta data.

        """
        text_content = self._get_text_content(article)
        summary = article["summary"]
        uuid = article["uuid"]
        canonical = article["canonical"]
        data = {
            "page": self.current_page,
            "canonical": canonical,
            "uuid": uuid,
            "text_content": text_content,
            "summary": summary,
        }
        return data

    @staticmethod
    def _get_text_content(article: dict) -> str:
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
