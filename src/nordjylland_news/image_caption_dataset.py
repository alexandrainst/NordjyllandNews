"""Class that builds the image caption dataset."""

from typing import Dict, List

from omegaconf import DictConfig

from .base_dataset_class import DataSetBuilder
from .utils import append_jsonl


class ImageCaptionDataSetBuilder(DataSetBuilder):
    """Builds dataset with images and captions.

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
        new_data (list of dict):
            New data to append to dataset.
    """

    def build_dataset(self) -> None:
        """Builds image caption dataset.

        Starts from page self.current_page. When a page is reached that has no articles,
        the method stops and returns None.
        """

        self.logger.info("Building image caption dataset")

        # Iterate over pages until a page with no articles is visited.
        while True:
            self.new_data: List[Dict] = []
            articles = self.get_page_with_articles(page=self.current_page)

            if self.dataset_done(articles):
                self.logger.info("Dataset done.")
                return
            else:
                # Iterate over articles on current page
                for article in articles:
                    # Appends image meta data to self.new_image_meta_data for every image with a caption in the article
                    self.get_image_data(article)

            # Append new data to dataset.
            append_jsonl(self.new_data, self.data_path)

            # Log progess
            # Most pages will contain 100 articles, but there are some exceptions.
            # The log might therefore not be exactly correct, but should give a good indication of progress.
            self.logger.info(
                f"{self.current_page * self.max_per_page}/{self.total_articles}"
            )

            self.page_increment()
            self.sleep()

    def get_image_data(self, article: dict) -> None:
        """Gets image meta data for every image with a caption in the article.

        Args:
            article (dict):
                Article data.
        """
        for content in article["content"]:
            if content["type"] == "Image":
                uuid = content["content"]["image_uuid"]
                caption = content["content"]["caption"]
                if uuid not in self.seen_uuids and caption is not None:
                    data = self._get_image_meta_data(content, article)
                    self.seen_uuids.add(uuid)
                    self.new_data.append(data)

    def _get_image_meta_data(self, content: dict, article: dict) -> dict:
        """Extract image meta data.

        Extract image meta data.
        Page number is added to meta data, as it will be used to determine the current page when the script is run again.

        Args:
            content (dict):
                Content data.
            article (dict):
                Article data.

        Returns:
            image_meta_data (dict):
                Image meta data.
        """
        canonical = article["canonical"]

        uuid = content["content"]["image_uuid"]
        download_url = content["content"]["image"]["download_url"]
        name = content["content"]["image"]["name"]
        caption = content["content"]["caption"]

        image_meta_data = {
            "page": self.current_page,
            "canonical": canonical,
            "uuid": uuid,
            "download_url": download_url,
            "name": name,
            "caption": caption,
        }
        return image_meta_data
