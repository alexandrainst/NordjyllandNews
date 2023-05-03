"""Unit tests for the `summary_dataset` module."""

import os

import pytest

from nordjylland_news.summary_dataset import SummaryDataSetBuilder

PAGE = 1


@pytest.fixture(scope="module")
def summary_builder(config):
    return SummaryDataSetBuilder(config)


def test_load_dataset(summary_builder):
    _ = summary_builder.load_dataset()
    assert os.path.exists(summary_builder.data_path)


def test_get_total_articles(summary_builder):
    total_articles = summary_builder.get_total_articles()
    assert total_articles > 0


@pytest.fixture(scope="module")
def articles(summary_builder):
    return summary_builder.get_page_with_articles(PAGE)


@pytest.fixture(scope="module")
def article(articles):
    return articles[0]


# mark.parametrize with keys below
@pytest.mark.parametrize(
    "key",
    [
        "uuid",
        "canonical",
        "summary",
        "content",
    ],
)
def test_article_keys(article, key):
    assert article[key]


@pytest.fixture(scope="module")
def article_content(article):
    return article["content"]


@pytest.mark.parametrize(
    "key",
    [
        "type",
    ],
)
def test_content_keys(article_content, key):
    assert all([key in d for d in article_content])


@pytest.mark.parametrize(
    "key",
    [
        "html",
    ],
)
def test_text_content_keys(article_content, key):
    assert all(
        [key in d["content"].keys() for d in article_content if d["type"] == "Text"]
    )


@pytest.mark.parametrize(
    "article, expected_data",
    [
        (
            {
                "uuid": "123",
                "canonical": "https://example.com/article",
                "summary": "This is a summary.",
                "content": [
                    {"type": "Text", "content": {"html": "<p>This is some text.</p>"}},
                    {
                        "type": "Image",
                        "content": {"url": "https://example.com/image.jpg"},
                    },
                ],
            },
            {
                "page": 1,
                "uuid": "123",
                "canonical": "https://example.com/article",
                "text_content": "This is some text.",
                "summary": "This is a summary.",
            },
        ),
    ],
)
def test_get_article_data(summary_builder, article, expected_data):
    data = summary_builder.get_article_data(article)
    assert data == expected_data


@pytest.mark.parametrize(
    "article, expected_text_content",
    [
        (
            {
                "content": [
                    {"type": "Text", "content": {"html": "<p>This is some text.</p>"}},
                    {
                        "type": "Image",
                        "content": {"url": "https://example.com/image.jpg"},
                    },
                ]
            },
            "This is some text.",
        ),
    ],
)
def test_summary_builder_get_text_content(
    summary_builder, article, expected_text_content
):
    text_content = summary_builder._get_text_content(article)
    assert text_content == expected_text_content
