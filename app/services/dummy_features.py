import random
from abc import ABC, abstractmethod
from datetime import UTC, datetime
from typing import Any


class DummyFeature(ABC):
    """Base class for dummy features"""

    def __init__(self, feature_name: str):
        self.feature_name = feature_name
        self.seed = abs(hash(feature_name)) % (2**31)

    @abstractmethod
    def generate_metadata(self, event_timestamp: int) -> dict[str, Any]:
        """Generate feature metadata"""


class DriverConvRateV1(DummyFeature):
    def generate_metadata(self, event_timestamp: int) -> dict[str, Any]:
        random.seed(self.seed)
        return {
            "feature_type": "real-time",
            "query_sql": "SELECT conv_rate FROM driver_hourly_stats WHERE driver_id = ?",
            "created_time": 1640995200000,  # Jan 1, 2022
            "updated_time": int(datetime.now(UTC).timestamp() * 1000),
            "created_by": "Fia",
            "last_updated_by": "Ludy",
            "feature_data_type": "float",
            "approved_by": "Endy",
            "feature_id": "driver_conv_rate_v1",
            "feature_category_id": "driver_hourly_stats",
            "status": "READY FOR TESTING",
            "description": "Conversion rate for driver",
            "event_timestamp": event_timestamp,
        }


class DriverAccRateV2(DummyFeature):
    def generate_metadata(self, event_timestamp: int) -> dict[str, Any]:
        random.seed(self.seed)
        return {
            "feature_type": "batch",
            "query_sql": "SELECT acc_rate FROM driver_hourly_stats WHERE driver_id = ?",
            "created_time": 1641081600000,  # Jan 2, 2022
            "updated_time": int(datetime.now(UTC).timestamp() * 1000),
            "created_by": "Ludy",
            "last_updated_by": "Eka",
            "feature_data_type": "integer",
            "approved_by": "Endy",
            "feature_id": "driver_acc_rate_v2",
            "feature_category_id": "driver_hourly_stats",
            "status": "APPROVED",
            "description": "Acceptance rate for driver",
            "event_timestamp": event_timestamp,
        }


class DriverAvgTripsV3(DummyFeature):
    def generate_metadata(self, event_timestamp: int) -> dict[str, Any]:
        random.seed(self.seed)
        return {
            "feature_type": "real-time",
            "query_sql": "SELECT avg_daily_trips FROM driver_hourly_stats WHERE driver_id = ?",
            "created_time": 1641168000000,  # Jan 3, 2022
            "updated_time": int(datetime.now(UTC).timestamp() * 1000),
            "created_by": "Eka",
            "last_updated_by": "Endy",
            "feature_data_type": "string",
            "approved_by": None,
            "feature_id": "driver_avg_trips_v3",
            "feature_category_id": "driver_hourly_stats",
            "status": None,
            "description": None,
            "event_timestamp": event_timestamp,
        }


class FraudAmountV1(DummyFeature):
    def generate_metadata(self, event_timestamp: int) -> dict[str, Any]:
        random.seed(self.seed)
        return {
            "feature_type": "batch",
            "query_sql": "SELECT fraud_amount FROM fraud_detection WHERE transaction_id = ?",
            "created_time": 1609459200000,  # Jan 1, 2021
            "updated_time": int(datetime.now(UTC).timestamp() * 1000),
            "created_by": "Security Team",
            "last_updated_by": "Fraud Analyst",
            "feature_data_type": "float",
            "approved_by": "Risk Manager",
            "feature_id": "fraud_amount_v1",
            "feature_category_id": "fraud",
            "status": "DEPLOYED",
            "description": "Fraud amount detection",
            "event_timestamp": event_timestamp,
        }


class CustomerIncomeV1(DummyFeature):
    def generate_metadata(self, event_timestamp: int) -> dict[str, Any]:
        random.seed(self.seed)
        return {
            "feature_type": "batch",
            "query_sql": "SELECT monthly_income FROM customer_profile WHERE customer_id = ?",
            "created_time": 1609545600000,  # Jan 2, 2021
            "updated_time": int(datetime.now(UTC).timestamp() * 1000),
            "created_by": "Data Team",
            "last_updated_by": "Analytics Team",
            "feature_data_type": "integer",
            "approved_by": "Product Manager",
            "feature_id": "customer_income_v1",
            "feature_category_id": "customer",
            "status": "APPROVED",
            "description": "Customer monthly income",
            "event_timestamp": event_timestamp,
        }


# Feature registry
FEATURE_REGISTRY = {
    "driver_hourly_stats:conv_rate:1": DriverConvRateV1("driver_hourly_stats:conv_rate:1"),
    "driver_hourly_stats:acc_rate:2": DriverAccRateV2("driver_hourly_stats:acc_rate:2"),
    "driver_hourly_stats:avg_daily_trips:3": DriverAvgTripsV3(
        "driver_hourly_stats:avg_daily_trips:3"
    ),
    # Keep original features
    "fraud:amount:v1": FraudAmountV1("fraud:amount:v1"),
    "customer:income:v1": CustomerIncomeV1("customer:income:v1"),
}
