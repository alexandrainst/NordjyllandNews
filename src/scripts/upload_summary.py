"""Upload the summary dataset to the HuggingFace Hub.

Usage:
    >>> python src/scripts/upload_summary.py
"""


from datasets import load_dataset

DATASET_FOLDER_PATH = (
    "../../../../../mnt/data_6tb/oliver/NordjyllandNews/data/processed/summary"
)
DATASET_HF_PATH = "oliverkinch/nordjylland-news-summarization"


dataset = load_dataset(DATASET_FOLDER_PATH)
dataset.push_to_hub(DATASET_HF_PATH, private=True)
