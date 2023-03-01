import os
from typing import Any, Dict

import pytest
from omegaconf import OmegaConf

from nordjylland_news.image_caption_dataset import ImageCaptionDataSetBuilder


@pytest.fixture(scope="session")
def builder():
    """Instantiate a SummaryDataSetBuilder object."""
    cfg = OmegaConf.load("config/config.yaml")
    data_setname = cfg["dataset_names"]["test"]
    return ImageCaptionDataSetBuilder(dataset_name=data_setname, cfg=cfg)


class TestAPIArticleData:
    def test_get_total_articles(self, builder: ImageCaptionDataSetBuilder):
        """Test the get_total_articles() method for the ImageCaptionDataSetBuilder class."""
        total_articles = builder.get_total_articles()
        assert total_articles > 0

    def test_get_page_with_articles(self, builder: ImageCaptionDataSetBuilder):
        """Test the get_page_with_articles() method for the ImageCaptionDataSetBuilder class."""
        page = 1
        articles = builder.get_page_with_articles(page)
        assert articles

        # Test that the article has the expected keys.
        article = articles[0]
        assert article["uuid"]
        assert article["canonical"]
        assert article["content"]

        # Keys used in get_image_data()
        all_content = article["content"]
        assert all(["type" in d for d in all_content])
        assert all(
            [
                "image_uuid" in content["content"].keys()
                for content in all_content
                if content["type"] == "Image"
            ]
        )
        assert all(
            [
                "caption" in content["content"].keys()
                for content in all_content
                if content["type"] == "Image"
            ]
        )

        assert all(
            [
                "image" in content["content"].keys()
                for content in all_content
                if content["type"] == "Image"
            ]
        )
        assert all(
            [
                "download_url" in content["content"]["image"].keys()
                for content in all_content
                if content["type"] == "Image"
            ]
        )
        assert all(
            [
                "name" in content["content"]["image"].keys()
                for content in all_content
                if content["type"] == "Image"
            ]
        )


class TestImageMetaDataExtraction:
    def test_get_image_meta_data(self, builder: ImageCaptionDataSetBuilder):
        """Test the _get_image_meta_data() method for the ImageCaptionDataSetBuilder class."""
        article: Dict[Any, Any] = {
            "uuid": "123",
            "canonical": "https://example.com/article",
            "content": [
                {
                    "type": "Image",
                    "content": {
                        "image_uuid": "456",
                        "image": {
                            "download_url": "https://example.com/image.jpg",
                            "name": "example_image.jpg",
                        },
                        "caption": "An example image",
                    },
                }
            ],
        }
        content = article["content"][0]
        expected_data = {
            "page": builder.current_page,
            "canonical": "https://example.com/article",
            "uuid": "456",
            "download_url": "https://example.com/image.jpg",
            "name": "example_image.jpg",
            "caption": "An example image",
        }
        data = builder._get_image_meta_data(content, article)
        assert data == expected_data

    def test_get_image_data(self, builder: ImageCaptionDataSetBuilder):
        """Test the get_image_data() method for the ImageCaptionDataSetBuilder class."""
        article = {
            "uuid": "123",
            "canonical": "https://example.com/article",
            "content": [
                {
                    "type": "Image",
                    "content": {
                        "image_uuid": "456",
                        "image": {
                            "download_url": "https://example.com/image.jpg",
                            "name": "example_image.jpg",
                        },
                        "caption": "An example image",
                    },
                }
            ],
        }
        builder.new_data = []
        builder.get_image_data(article)
        expected_data = [
            {
                "page": 1,
                "canonical": "https://example.com/article",
                "uuid": "456",
                "download_url": "https://example.com/image.jpg",
                "name": "example_image.jpg",
                "caption": "An example image",
            }
        ]
        assert builder.new_data == expected_data


class TestSummaryBuilder:
    def test_summary_builder_build_dataset(self, builder: ImageCaptionDataSetBuilder):
        """Test the build_dataset() method for the ImageCaptionDataSetBuilder class."""
        builder.build_dataset()
        assert builder.seen_uuids
        assert builder.current_page > 1

        # Remove test data
        test_data_path = builder.data_path
        if os.path.exists(test_data_path):
            os.remove(test_data_path)


if __name__ == "__main__":
    config = OmegaConf.load("config/config.yaml")
    data_setname = config["dataset_names"]["test"]
    image_caption_builder = ImageCaptionDataSetBuilder(dataset_name="test", cfg=config)
    t = TestAPIArticleData()
    t.test_get_page_with_articles(image_caption_builder)
