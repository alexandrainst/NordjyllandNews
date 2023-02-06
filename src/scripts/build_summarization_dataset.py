import argparse

from nordjylland_news.summary_data_set import SummaryDataSetBuilder


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--total_articles", type=int, default=500)
    args = parser.parse_args()

    total_articles = args.total_articles

    print("...Building data set with total samples:", total_articles)

    builder = SummaryDataSetBuilder()
    builder.build_data_set(total_articles=total_articles)


if __name__ == "__main__":
    main()
