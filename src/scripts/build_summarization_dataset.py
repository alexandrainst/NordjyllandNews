"""Script that builds the summarisation dataset.

Usage:
    >>> python src/scripts/build_summarization_dataset.py
"""

import hydra
from omegaconf import DictConfig

from nordjylland_news.summary_dataset import SummaryDataSetBuilder


@hydra.main(config_path="../../config", config_name="config.yaml")
def main(cfg: DictConfig) -> None:
    dataset_name = cfg["dataset_names"]["summary_dataset"]
    builder = SummaryDataSetBuilder(dataset_name=dataset_name, cfg=cfg)
    builder.build_dataset()


if __name__ == "__main__":
    main()
