"""Upload the summary dataset to the HuggingFace Hub.

Usage:
    >>> python src/scripts/upload_summary.py
"""


from datasets import load_dataset

# Number of samples for each split are from notebooks/process_summary_data.ipynb
TRAIN_LENGTH = 75219
VAL_LENGTH = 4178
TEST_LENGTH = 4178

DATASET_FOLDER_PATH = (
    "../../../../../mnt/data_6tb/oliver/NordjyllandNews/data/processed/summary"
)
DATASET_HF_PATH = "alexandrainst/nordjylland-news-summarization"

data_files = dict(
    train=DATASET_FOLDER_PATH + "/train.jsonl",
    val=DATASET_FOLDER_PATH + "/val.jsonl",
    test=DATASET_FOLDER_PATH + "/test.jsonl",
)
dataset = load_dataset("json", data_files=data_files)

assert len(dataset["train"]) == 75219
assert len(dataset["val"]) == 4178
assert len(dataset["test"]) == 4178

dataset.push_to_hub(DATASET_HF_PATH, private=False)
