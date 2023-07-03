"""Unit tests for the `image_caption_dataset` module."""

import pytest

from nordjylland_news.image_caption_dataset import ImageCaptionDataSetBuilder


@pytest.fixture(scope="module")
def image_caption_builder(config):
    return ImageCaptionDataSetBuilder(config)


def test_get_total_articles(image_caption_builder):
    total_articles = image_caption_builder.get_total_articles()
    assert total_articles > 0


@pytest.fixture(scope="module")
def articles(image_caption_builder, page):
    return image_caption_builder.get_page_with_articles(page)


@pytest.fixture(scope="module")
def article(articles):
    return articles[0]


def test_articles(articles):
    assert articles


@pytest.mark.parametrize(
    "key",
    [
        "uuid",
        "canonical",
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
        "caption",
        "image_uuid",
        "image",
    ],
)
def test_image_content_keys(article_content, key):
    assert all(
        [
            key in content["content"].keys()
            for content in article_content
            if content["type"] == "Image"
        ]
    )


@pytest.mark.parametrize(
    "key",
    [
        "download_url",
        "name",
    ],
)
def test_article_content_image_keys(article_content, key):
    assert all(
        [
            key in content["content"]["image"].keys()
            for content in article_content
            if content["type"] == "Image"
        ]
    )


@pytest.mark.parametrize(
    "article, expected_data",
    [
        (
            {
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
            },
            {
                "page": 1,
                "canonical": "https://example.com/article",
                "uuid": "456",
                "download_url": "https://example.com/image.jpg",
                "name": "example_image.jpg",
                "caption": "An example image",
                "file_name": "data/raw/images/train/1.jpg",
            },
        ),
    ],
)
def test_get_image_meta_data(image_caption_builder, article, expected_data):
    content = article["content"][0]
    data = image_caption_builder._get_image_meta_data(content, article)
    assert data == expected_data


@pytest.mark.parametrize(
    "article, expected_data",
    [
        (
            {
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
            },
            [
                {
                    "page": 1,
                    "canonical": "https://example.com/article",
                    "uuid": "456",
                    "download_url": "https://example.com/image.jpg",
                    "name": "example_image.jpg",
                    "caption": "An example image",
                    "file_name": "data/raw/images/train/1.jpg",
                }
            ],
        ),
    ],
)
def test_get_image_data(image_caption_builder, article, expected_data):
    image_caption_builder.new_data = []
    image_caption_builder.get_image_data(article, download_images=False)
    assert image_caption_builder.new_data == expected_data
