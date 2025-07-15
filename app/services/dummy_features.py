from abc import ABC, abstractmethod
from typing import Any


# Abstract base metadata
class DummyFeatureMetadata(ABC):
    def __init__(self, feature_name: str) -> None:
        self.feature_name = feature_name

    @abstractmethod
    def generate_metadata(self, timestamp: int) -> dict[str, Any]:
        pass


# Driver conversion rate metadata
class DriverConvRateV1(DummyFeatureMetadata):
    def generate_metadata(self, timestamp: int) -> dict[str, Any]:
        return {
            "feature_type": "real-time",
            "feature_data_type": "float",
            "query": "SELECT conv_rate FROM driver_hourly_stats WHERE driver_id = ?",
            "created_time": timestamp,
            "updated_time": timestamp,
            "deleted_time": None,
            "created_by": "Fia",
            "last_updated_by": "Ludy",
            "deleted_by": None,
            "approved_by": "Endy",
            "status": "DEPLOYED",
            "description": "Conversion rate for driver",
        }


# Driver acceptance rate metadata
class DriverAccRateV2(DummyFeatureMetadata):
    def generate_metadata(self, timestamp: int) -> dict[str, Any]:
        return {
            "feature_type": "batch",
            "feature_data_type": "integer",
            "query": "SELECT acc_rate FROM driver_hourly_stats WHERE driver_id = ?",
            "created_time": 1641081600000,
            "updated_time": timestamp,
            "deleted_time": None,
            "created_by": "Ludy",
            "last_updated_by": "Eka",
            "deleted_by": None,
            "approved_by": "Endy",
            "status": "APPROVED",
            "description": "Acceptance rate for driver",
        }


# Driver avg daily trips metadata
class DriverAvgTripsV3(DummyFeatureMetadata):
    def generate_metadata(self, timestamp: int) -> dict[str, Any]:
        return {
            "feature_type": "real-time",
            "feature_data_type": "string",
            "query": "SELECT avg_trips FROM driver_hourly_stats WHERE driver_id = ?",
            "created_time": timestamp,
            "updated_time": timestamp,
            "deleted_time": timestamp,
            "created_by": "Eka",
            "last_updated_by": "Fia",
            "deleted_by": "Endy",
            "approved_by": "Endy",
            "status": "DELETED",
            "description": "Average daily trips",
        }


# Fraud amount metadata
class FraudAmountV1(DummyFeatureMetadata):
    def generate_metadata(self, timestamp: int) -> dict[str, Any]:
        return {
            "feature_type": "real-time",
            "feature_data_type": "float",
            "query": "SELECT amount FROM fraud WHERE transaction_id = ?",
            "created_time": timestamp,
            "updated_time": timestamp,
            "deleted_time": None,
            "created_by": "Fia",
            "last_updated_by": "Ludy",
            "deleted_by": None,
            "approved_by": "Endy",
            "status": "DEPLOYED",
            "description": "Fraud amount for transaction",
        }


# Customer income metadata
class CustomerIncomeV1(DummyFeatureMetadata):
    def generate_metadata(self, timestamp: int) -> dict[str, Any]:
        return {
            "feature_type": "batch",
            "feature_data_type": "float",
            "query": "SELECT income FROM customer_profile WHERE customer_id = ?",
            "created_time": timestamp,
            "updated_time": timestamp,
            "deleted_time": None,
            "created_by": "Ludy",
            "last_updated_by": "Eka",
            "deleted_by": None,
            "approved_by": "Endy",
            "status": "APPROVED",
            "description": "Customer income",
        }


# Metadata registry
FEATURE_METADATA_REGISTRY: dict[str, dict[str, Any]] = {
    "driver_hourly_stats:conv_rate:1": {
        "class": DriverConvRateV1,
        "type": "real-time",
        "description": "Conversion rate for driver",
    },
    "driver_hourly_stats:acc_rate:2": {
        "class": DriverAccRateV2,
        "type": "batch",
        "description": "Acceptance rate for driver",
    },
    "driver_hourly_stats:avg_daily_trips:3": {
        "class": DriverAvgTripsV3,
        "type": "real-time",
        "description": "Average daily trips",
    },
    "fraud:amount:v1": {
        "class": FraudAmountV1,
        "type": "real-time",
        "description": "Fraud amount for transaction",
    },
    "customer:income:v1": {
        "class": CustomerIncomeV1,
        "type": "batch",
        "description": "Customer income",
    },
}
