"""Upload the image captioning dataset to the HuggingFace Hub.

Usage:
    >>> python src/scripts/upload_image_captioning.py
"""


from datasets import load_dataset

DATASET_PATH = (
    "../../../../../mnt/data_6tb/oliver/NordjyllandNews/data/processed/images/train"
)
DATASET_HF_PATH = "oliverkinch/nordjylland-news-image-captioning"

dataset = load_dataset("imagefolder", data_dir=DATASET_PATH, split="train")
dataset.push_to_hub(DATASET_HF_PATH, private=True)
