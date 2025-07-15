import pytest

from app.utils.timestamp import (
    format_timestamp,
    get_current_timestamp,
    timestamp_to_datetime,
    validate_timestamp,
)


class TestTimestampUtils:
    # Get current timestamp
    def test_get_current_timestamp(self):
        ts = get_current_timestamp()
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

    # Format timestamp
    def test_format_timestamp(self):
        ts = 1640995200000
        assert "2022-01-01" in format_timestamp(ts)
        result = format_timestamp(-1)
        assert result == "Invalid timestamp" or result.startswith("1969-12-31T23:59:59")

    # Format timestamp invalid
    def test_format_timestamp_invalid(self):
        assert format_timestamp("not_an_int") == "Invalid timestamp"
