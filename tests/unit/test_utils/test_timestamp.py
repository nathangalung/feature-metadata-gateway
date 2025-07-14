from datetime import UTC, datetime

import pytest

from app.utils.timestamp import (
    add_milliseconds,
    datetime_to_timestamp,
    format_datetime,
    format_timestamp,
    get_current_timestamp,
    get_current_timestamp_ms,
    get_time_difference_ms,
    get_timestamp_from_datetime,
    get_timestamp_range,
    get_utc_timestamp,
    is_valid_timestamp,
    normalize_timestamp,
    parse_timestamp,
    subtract_milliseconds,
    timestamp_to_datetime,
    validate_timestamp,
)


class TestTimestampUtils:
    """Test timestamp utility functions."""

    # Get current timestamp
    def test_get_current_timestamp(self):
        ts = get_current_timestamp()
        assert isinstance(ts, int)
        assert ts > 0

    # Get current timestamp ms
    def test_get_current_timestamp_ms(self):
        ts = get_current_timestamp_ms()
        assert isinstance(ts, int)
        assert ts > 0

    # Timestamp to datetime
    def test_timestamp_to_datetime(self):
        ts = 1640995200000
        dt = timestamp_to_datetime(ts)
        assert dt.year == 2022

    # Invalid type for timestamp
    def test_timestamp_to_datetime_invalid_type(self):
        with pytest.raises(ValueError):
            timestamp_to_datetime("not_an_int")

    # Small value timestamp
    def test_timestamp_to_datetime_small_value(self):
        ts = 1640995200
        dt = timestamp_to_datetime(ts)
        assert dt.year == 2022

    # Negative timestamp
    def test_timestamp_to_datetime_negative(self):
        dt = timestamp_to_datetime(-123456789)
        assert dt.year < 1970

    # Validate timestamp
    def test_validate_timestamp(self):
        assert validate_timestamp(1640995200000)
        assert not validate_timestamp(None)

    # Is valid timestamp
    def test_is_valid_timestamp(self):
        assert is_valid_timestamp(1640995200000)
        assert not is_valid_timestamp(-1)

    # Is valid timestamp exception
    def test_is_valid_timestamp_exception(self):
        from unittest.mock import patch

        with patch(
            "app.utils.timestamp.timestamp_to_datetime", side_effect=Exception("fail")
        ):
            assert not is_valid_timestamp(1640995200000)

    # Time difference ms
    def test_get_time_difference_ms(self):
        assert get_time_difference_ms(1000, 2000) == 1000

    # Add/subtract milliseconds
    def test_add_subtract_milliseconds(self):
        ts = 1000
        assert add_milliseconds(ts, 500) == 1500
        assert subtract_milliseconds(ts, 500) == 500

    # Format timestamp
    def test_format_timestamp(self):
        ts = 1640995200000
        assert "2022-01-01" in format_timestamp(ts)
        result = format_timestamp(-1)
        assert result == "Invalid timestamp" or result.startswith("1969-12-31T23:59:59")

    # Format timestamp invalid
    def test_format_timestamp_invalid(self):
        assert format_timestamp("not_an_int") == "Invalid timestamp"

    # Format datetime
    def test_format_datetime(self):
        dt = datetime(2022, 1, 1, tzinfo=UTC)
        assert "2022-01-01" in format_datetime(dt)

    # Parse timestamp
    def test_parse_timestamp(self):
        iso = "2022-01-01T00:00:00+00:00"
        assert parse_timestamp(iso) == 1640995200000

    # Parse timestamp invalid
    def test_parse_timestamp_invalid(self):
        with pytest.raises(ValueError):
            parse_timestamp("not-a-timestamp")
        with pytest.raises(ValueError):
            parse_timestamp("2022-13-01T00:00:00Z")
        with pytest.raises(ValueError):
            parse_timestamp("2022-01-01T25:00:00Z")

    # Normalize timestamp
    def test_normalize_timestamp(self):
        assert normalize_timestamp(1640995200000) == 1640995200000
        assert normalize_timestamp(1640995200) == 1640995200000
        assert normalize_timestamp(-100) == -100000
        assert normalize_timestamp(0) == 0
        assert normalize_timestamp(9999999999999) == 9999999999999

    # Get UTC timestamp
    def test_get_utc_timestamp(self):
        ts = get_utc_timestamp()
        assert isinstance(ts, int)

    # Get timestamp from datetime
    def test_get_timestamp_from_datetime(self):
        dt = datetime(2022, 1, 1, tzinfo=UTC)
        assert get_timestamp_from_datetime(dt) == 1640995200000

    # Get timestamp range
    def test_get_timestamp_range(self):
        start, end = get_timestamp_range(1, 0)
        assert start < end

    # Datetime to timestamp
    def test_datetime_to_timestamp(self):
        dt = datetime(2022, 1, 1, tzinfo=UTC)
        assert datetime_to_timestamp(dt) == 1640995200000
