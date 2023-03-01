"""Script that builds the image caption dataset.

Usage:
    >>> python src/scripts/build_image_caption_dataset.py
"""

import hydra
from omegaconf import DictConfig

from nordjylland_news.image_caption_dataset import ImageCaptionDataSetBuilder


@hydra.main(config_path="../../config", config_name="config.yaml")
def main(cfg: DictConfig):
    dataset_name = cfg["dataset_names"]["image_caption"]
    builder = ImageCaptionDataSetBuilder(dataset_name=dataset_name, cfg=cfg)
    builder.build_dataset()


if __name__ == "__main__":
    main()
