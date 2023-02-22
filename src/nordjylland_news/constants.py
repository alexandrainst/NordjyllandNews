"""Constants."""

# https://developer.bazo.dk/#876ab6f9-e057-43e3-897a-1563de34397e
HEADERS = {"Accept": "application/json", "Authorization": "centered"}

# Status codes
STATUS_CODE_OK = 200
TOO_MANY_REQUESTS = 429
ERROR_500 = 500

# Sleep times
SLEEP_SHORT = 5  # 5 seconds
SLEEP_MEDIUM = 60  # 1 minute
SLEEP_LONG = 900  # 15 minutes
