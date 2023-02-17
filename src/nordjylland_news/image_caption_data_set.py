"""Class that builds the image caption dataset."""

import os
import time
from typing import Dict, List

from .constants import (
    IMAGE_CAPTION_DATA_SET,
    MAX_PER_PAGE,
    RAW_DATA_PATH,
    SLEEP_60_SECONDS,
)
from .utils import (
    append_jsonl,
    get_page_with_articles_data,
    get_total_articles,
    init_jsonl,
    load_jsonl,
)


class ImageCaptionDataSetBuilder:
    """Builds data set with images and captions."""

    def __init__(self) -> None:
        # Get total number of articles
        self.total_articles = get_total_articles()

        # Init remaining attributes
        self.init()

    def init(self) -> None:
        """Initialize class attributes.

        Sets self.current_page to the last page in the data set, or 1 if the data set is empty.
        Sets self.seen_uuids to a set of all uuids in the data set.
        """
        # Init/Load data set
        if not os.path.exists(RAW_DATA_PATH[IMAGE_CAPTION_DATA_SET]):
            init_jsonl(RAW_DATA_PATH[IMAGE_CAPTION_DATA_SET])
        data = load_jsonl(RAW_DATA_PATH[IMAGE_CAPTION_DATA_SET])

        # Get page number of last article in data set. If data set is empty, set page to 1.
        self.current_page = data[-1]["page"] if data else 1

        # Get all uuids in data set
        self.seen_uuids = set(d["uuid"] for d in data)

    def build_data_set(self) -> None:
        """Builds image caption data set.

        Starts from page self.current_page. When a page is reached that has no articles, the method stops and returns None.
        """
        # Iterate over pages until a page with no articles is visited.
        while True:
            self.new_image_meta_data: List[Dict] = []
            articles_data = get_page_with_articles_data(page=self.current_page)

            # Check if there are no more articles to process.
            # If the `articles_data` list is empty, it means that the previous page was
            # the last page containing articles. In this case, stop processing and return None.
            if not articles_data:
                print("No more articles")
                print("Page: ", self.current_page)
                return None
            else:
                # Iterate over articles on current page
                for article_data in articles_data:
                    # Appends image meta data to self.new_image_meta_data for every image with a caption in the article
                    self.get_image_data(article_data)

            # Append new data to data set.
            append_jsonl(
                self.new_image_meta_data, RAW_DATA_PATH[IMAGE_CAPTION_DATA_SET]
            )

            # Print number of articles processed.
            # Most pages will contain 100 articles, but there are some exceptions.
            # The print might therefore not be exactly correct, but should give a good indication of progress.
            print(
                f"Articles processed: {self.current_page * MAX_PER_PAGE}/{self.total_articles}"
            )

            # Sleep to avoid getting blocked by the API.
            time.sleep(SLEEP_60_SECONDS)

            # Go to next page.
            self.current_page += 1

    def get_image_data(self, article_data: dict) -> None:
        """Gets image meta data for every image with a caption in the article.

        Args:
            article_data (dict):
                Article data.
        """
        for content in article_data["content"]:

            # Check if content is an image with a caption.
            if (
                content["type"] == "Image"
                and content["content"]["caption"] is not None
                and content["content"]["image_uuid"] not in self.seen_uuids
            ):
                image_meta_data = self._get_image_meta_data(content, article_data)
                self.seen_uuids.add(image_meta_data["uuid"])
                self.new_image_meta_data.append(image_meta_data)

    def _get_image_meta_data(self, content: dict, article_data: dict) -> dict:
        """Extract image meta data.

        Extract image meta data.
        Page number is added to meta data, as it will be used to determine the current page when the script is run again.

        Args:
            content (dict):
                Content data.
            article_data (dict):
                Article data.

        Returns:
            image_meta_data (dict):
                Image meta data.
        """
        canonical = article_data["canonical"]

        uuid = content["content"]["image_uuid"]
        download_url = content["content"]["image"]["download_url"]
        name = content["content"]["image"]["name"]
        caption = content["content"]["caption"]

        image_meta_data = {
            "canonical": canonical,
            "uuid": uuid,
            "download_url": download_url,
            "name": name,
            "caption": caption,
            "page": self.current_page,
        }
        return image_meta_data
