"""Timestamp utilities for the application."""

import time
from datetime import UTC, datetime, timedelta


def get_current_timestamp() -> int:
    """Current timestamp ms."""
    return int(time.time() * 1000)

def get_current_timestamp_ms() -> int:
    """Current timestamp ms (alias)."""
    return get_current_timestamp()

def timestamp_to_datetime(timestamp: int) -> datetime:
    """Timestamp to datetime."""
    if not isinstance(timestamp, int):
        raise ValueError("Timestamp must be int")
    if timestamp > 10**10:
        return datetime.fromtimestamp(timestamp / 1000, tz=UTC)
    return datetime.fromtimestamp(timestamp, tz=UTC)

def validate_timestamp(timestamp: int | None) -> bool:
    """Validate timestamp."""
    return is_valid_timestamp(timestamp)

def is_valid_timestamp(timestamp: int | None) -> bool:
    """Check timestamp validity."""
    if timestamp is None or not isinstance(timestamp, int) or timestamp <= 0:
        return False
    try:
        dt = timestamp_to_datetime(timestamp)
        now = datetime.now(UTC)
        min_date = datetime(1970, 1, 1, tzinfo=UTC)
        max_date = datetime(now.year + 100, 12, 31, tzinfo=UTC)
        return min_date <= dt <= max_date
    except Exception:
        return False

def get_time_difference_ms(start_timestamp: int, end_timestamp: int) -> int:
    """Time diff ms."""
    return abs(end_timestamp - start_timestamp)

def add_milliseconds(timestamp: int, milliseconds: int) -> int:
    """Add ms to timestamp."""
    return timestamp + milliseconds

def subtract_milliseconds(timestamp: int, milliseconds: int) -> int:
    """Subtract ms from timestamp."""
    return timestamp - milliseconds

def format_timestamp(timestamp: int) -> str:
    """Format timestamp ISO."""
    try:
        dt = timestamp_to_datetime(timestamp)
        return dt.isoformat()
    except Exception:
        return "Invalid timestamp"

def format_datetime(dt: datetime) -> str:
    """Format datetime ISO."""
    return dt.isoformat()

def parse_timestamp(timestamp_str: str) -> int:
    """Parse ISO string to ms."""
    try:
        if timestamp_str.endswith('Z'):
            dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        else:
            dt = datetime.fromisoformat(timestamp_str)
        return int(dt.timestamp() * 1000)
    except Exception:
        raise ValueError("Invalid timestamp format")

def normalize_timestamp(timestamp: int) -> int:
    """Normalize to ms."""
    if timestamp < 10**10:
        return timestamp * 1000
    return timestamp

def get_utc_timestamp() -> int:
    """Current UTC timestamp ms."""
    return get_current_timestamp()

def get_timestamp_from_datetime(dt: datetime) -> int:
    """Datetime to ms."""
    return int(dt.timestamp() * 1000)

def get_timestamp_range(start_days_ago: int, end_days_ago: int = 0) -> tuple[int, int]:
    """Timestamp range for days."""
    now = datetime.now(UTC)
    start_dt = now - timedelta(days=start_days_ago)
    end_dt = now - timedelta(days=end_days_ago)
    return (get_timestamp_from_datetime(start_dt), get_timestamp_from_datetime(end_dt))

def datetime_to_timestamp(dt: datetime) -> int:
    """Datetime to ms."""
    return get_timestamp_from_datetime(dt)
