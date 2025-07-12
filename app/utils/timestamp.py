import datetime
from typing import Any


def get_current_timestamp() -> int:
    return int(datetime.datetime.now(datetime.UTC).timestamp() * 1000)


def get_current_timestamp_ms() -> int:
    return int(datetime.datetime.now(datetime.UTC).timestamp() * 1000)


def timestamp_to_datetime(ts: int) -> datetime.datetime:
    if not isinstance(ts, int):
        raise ValueError("Timestamp must be int")
    # Accept both ms and s
    if ts > 1e12:
        return datetime.datetime.fromtimestamp(ts / 1000, tz=datetime.UTC)
    return datetime.datetime.fromtimestamp(ts, tz=datetime.UTC)


def validate_timestamp(ts: Any) -> bool:
    try:
        timestamp_to_datetime(ts)
        return True
    except Exception:
        return False


def is_valid_timestamp(ts: Any) -> bool:
    try:
        dt = timestamp_to_datetime(ts)
        return dt.year > 1970
    except Exception:
        return False


def get_time_difference_ms(start: int, end: int) -> int:
    return end - start


def add_milliseconds(ts: int, ms: int) -> int:
    return ts + ms


def subtract_milliseconds(ts: int, ms: int) -> int:
    return ts - ms


def format_timestamp(ts: int) -> str:
    try:
        dt = timestamp_to_datetime(ts)
        return dt.isoformat()
    except Exception:
        return "Invalid timestamp"


def format_datetime(dt: datetime.datetime) -> str:
    return dt.isoformat()


def parse_timestamp(iso: str) -> int:
    try:
        dt = datetime.datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return int(dt.timestamp() * 1000)
    except Exception as e:
        raise ValueError("Invalid timestamp format") from e


def normalize_timestamp(timestamp: int) -> int:
    # If it's in seconds, convert to ms
    if abs(timestamp) < 1e11:
        return timestamp * 1000
    return timestamp


def get_utc_timestamp() -> int:
    return int(datetime.datetime.now(datetime.UTC).timestamp() * 1000)


def get_timestamp_from_datetime(dt: datetime.datetime) -> int:
    return int(dt.timestamp() * 1000)


def get_timestamp_range(start: int, end: int) -> tuple[int, int]:
    if start > end:
        start, end = end, start
    return start, end


def datetime_to_timestamp(dt: datetime.datetime) -> int:
    return int(dt.timestamp() * 1000)
