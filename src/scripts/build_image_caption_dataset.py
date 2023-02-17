"""Script that builds the image caption dataset.

Usage:
    >>> python src/scripts/build_image_caption_dataset.py
"""

from nordjylland_news.image_caption_data_set import ImageCaptionDataSetBuilder


def main():
    print("...Building image caption data set")

    builder = ImageCaptionDataSetBuilder()
    builder.build_data_set()


if __name__ == "__main__":
    main()
