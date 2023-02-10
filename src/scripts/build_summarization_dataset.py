"""Script that builds the summarisation dataset.
Usage:
    >>> python src/scripts/build_summarization_dataset.py

    We can also specify the total number of articles, that we want in the data set (default is 500):
    >>> python src/scripts/build_summarization_dataset.py --total_articles 1000

    As of 10 Feb 2023, there are a total of 80892 articles. To obtain a data set of all articles, run:
    >>> python src/scripts/build_summarization_dataset.py --total_articles 80892
"""

import argparse

from nordjylland_news.summary_data_set import SummaryDataSetBuilder


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--total_articles", type=int, default=500)
    args = parser.parse_args()

    total_articles = args.total_articles

    print("...Building data set with total samples:", total_articles)

    builder = SummaryDataSetBuilder()
    builder.build_data_set(total_articles=total_articles)


if __name__ == "__main__":
    main()
