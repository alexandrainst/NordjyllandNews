"""Upload the image captioning dataset to the HuggingFace Hub.

Usage:
    >>> python src/scripts/upload_image_captioning.py
"""


from datasets import load_dataset

DATASET_PATH = "/mnt/data_6tb/oliver/NordjyllandNews/data/processed/images/train"
DATASET_HF_PATH = "alexandrainst/nordjylland-news-image-captioning"


def main() -> None:
    dataset = load_dataset("imagefolder", data_dir=DATASET_PATH, split="train")
    dataset.push_to_hub(DATASET_HF_PATH, private=True)


if __name__ == "__main__":
    main()
