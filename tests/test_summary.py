import os

import pytest
from omegaconf import OmegaConf

from nordjylland_news.summary_dataset import SummaryDataSetBuilder


@pytest.fixture(scope="session")
def builder():
    """Instantiate a SummaryDataSetBuilder object."""
    cfg = OmegaConf.load("config/config.yaml")
    data_setname = cfg["dataset_names"]["test"]
    return SummaryDataSetBuilder(dataset_name=data_setname, cfg=cfg)


class TestAPIArticleData:
    def test_get_total_articles(self, builder: SummaryDataSetBuilder):
        """Test the get_total_articles() method for the SummaryDataSetBuilder class."""
        total_articles = builder.get_total_articles()
        assert total_articles > 0

    def test_get_page_with_articles(self, builder: SummaryDataSetBuilder):
        """Test the get_page_with_articles() method for the SummaryDataSetBuilder class, and test that an article has the expected keys."""
        page = 1
        articles = builder.get_page_with_articles(page)
        assert articles

        # Test that the article has the expected keys.
        article = articles[0]
        assert article["uuid"]
        assert article["canonical"]
        assert article["summary"]
        assert article["content"]
        assert all(["type" in d for d in article["content"]])

        # Keys used in _get_text_content()
        assert all(["type" in d for d in article["content"]])
        assert all(
            [
                "html" in content["content"].keys()
                for content in article["content"]
                if content["type"] == "Text"
            ]
        )


class TestArticleDataExtraction:
    def test_get_article_data(self, builder: SummaryDataSetBuilder):
        """Test the get_article_data() method for the SummaryDataSetBuilder class."""
        article = {
            "uuid": "123",
            "canonical": "https://example.com/article",
            "summary": "This is a summary.",
            "content": [
                {"type": "Text", "content": {"html": "<p>This is some text.</p>"}},
                {"type": "Image", "content": {"url": "https://example.com/image.jpg"}},
            ],
        }
        expected_data = {
            "page": 1,
            "uuid": "123",
            "canonical": "https://example.com/article",
            "text_content": "This is some text.",
            "summary": "This is a summary.",
        }
        data = builder.get_article_data(article)
        assert data == expected_data

    def test_summary_builder_get_text_content(self, builder: SummaryDataSetBuilder):
        """Test the _get_text_content() for the SummaryDataSetBuilder class."""
        article = {
            "content": [
                {"type": "Text", "content": {"html": "<p>This is some text.</p>"}},
                {"type": "Image", "content": {"url": "https://example.com/image.jpg"}},
            ]
        }
        text_content = builder._get_text_content(article)
        assert text_content == "This is some text."


class TestSummaryBuilder:
    def test_summary_builder_build_dataset(self, builder: SummaryDataSetBuilder):
        """Test the build_dataset() method for the SummaryDataSetBuilder class."""
        builder.build_dataset()
        assert builder.dataset_length > 0
        assert builder.seen_uuids
        assert builder.current_page > 1

        # Remove test data
        test_data_path = builder.data_path
        if os.path.exists(test_data_path):
            os.remove(test_data_path)


if __name__ == "__main__":
    config = OmegaConf.load("config/config.yaml")
    data_setname = config["dataset_names"]["test"]
    summary_builder = SummaryDataSetBuilder(dataset_name="test", cfg=config)
    t = TestAPIArticleData()
    t.test_get_page_with_articles(summary_builder)
