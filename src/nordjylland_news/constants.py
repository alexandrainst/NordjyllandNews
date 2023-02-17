"""Constants."""

ARTICLES_API_URL = "https://public.nord.bazo.dk/v1/articles"

# Max articles per page
MAX_PER_PAGE = 100

# Data set names
SUMMARY_DATA_SET = "summary"
IMAGE_CAPTION_DATA_SET = "image_caption"

# Path to raw data
RAW_DATA_PATH = {
    SUMMARY_DATA_SET: "data/raw/summary.jsonl",
    IMAGE_CAPTION_DATA_SET: "data/raw/image_caption.jsonl",
}

# https://developer.bazo.dk/#876ab6f9-e057-43e3-897a-1563de34397e
HEADERS = {"Accept": "application/json", "Authorization": "centered"}

# Status codes
STATUS_CODE_OK = 200
TOO_MANY_REQUESTS = 429
ERROR_500 = 500

# Sleep time
SLEEP_5_SECONDS = 5
SLEEP_60_SECONDS = 60
SLEEP_15_MINUTES = 900
