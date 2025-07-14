import datetime
from typing import Any


# Get current timestamp ms
def get_current_timestamp() -> int:
    return int(datetime.datetime.now(datetime.UTC).timestamp() * 1000)


# Get current timestamp ms (alias)
def get_current_timestamp_ms() -> int:
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


# Check if timestamp is valid
def is_valid_timestamp(ts: Any) -> bool:
    try:
        dt = timestamp_to_datetime(ts)
        return dt.year > 1970
    except Exception:
        return False


# Time difference in ms
def get_time_difference_ms(start: int, end: int) -> int:
    return end - start


# Add ms to timestamp
def add_milliseconds(ts: int, ms: int) -> int:
    return ts + ms


# Subtract ms from timestamp
def subtract_milliseconds(ts: int, ms: int) -> int:
    return ts - ms


# Format timestamp as ISO string
def format_timestamp(ts: int) -> str:
    try:
        dt = timestamp_to_datetime(ts)
        return dt.isoformat()
    except Exception:
        return "Invalid timestamp"


# Format datetime as ISO string
def format_datetime(dt: datetime.datetime) -> str:
    return dt.isoformat()


# Parse ISO string to timestamp
def parse_timestamp(iso: str) -> int:
    try:
        dt = datetime.datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return int(dt.timestamp() * 1000)
    except Exception as e:
        raise ValueError("Invalid timestamp format") from e


# Normalize timestamp to ms
def normalize_timestamp(timestamp: int) -> int:
    if abs(timestamp) < 1e11:
        return timestamp * 1000
    return timestamp


# Get current UTC timestamp ms
def get_utc_timestamp() -> int:
    return int(datetime.datetime.now(datetime.UTC).timestamp() * 1000)


# Datetime to timestamp ms
def get_timestamp_from_datetime(dt: datetime.datetime) -> int:
    return int(dt.timestamp() * 1000)


# Get timestamp range tuple
def get_timestamp_range(start: int, end: int) -> tuple[int, int]:
    if start > end:
        start, end = end, start
    return start, end


# Datetime to timestamp ms (alias)
def datetime_to_timestamp(dt: datetime.datetime) -> int:
    return int(dt.timestamp() * 1000)
