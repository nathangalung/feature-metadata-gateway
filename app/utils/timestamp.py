import datetime
from typing import Any


# Get current timestamp ms
def get_current_timestamp() -> int:
    return int(datetime.datetime.now(datetime.UTC).timestamp() * 1000)


# Convert timestamp to datetime
def timestamp_to_datetime(ts: int) -> datetime.datetime:
    if not isinstance(ts, int):
        raise ValueError("Timestamp must be int")
    if ts > 1e12:
        return datetime.datetime.fromtimestamp(ts / 1000, tz=datetime.UTC)
    return datetime.datetime.fromtimestamp(ts, tz=datetime.UTC)


# Validate timestamp format
def validate_timestamp(ts: Any) -> bool:
    try:
        timestamp_to_datetime(ts)
        return True
    except Exception:
        return False


# Format timestamp as ISO string
def format_timestamp(ts: int) -> str:
    try:
        dt = timestamp_to_datetime(ts)
        return dt.isoformat()
    except Exception:
        return "Invalid timestamp"
