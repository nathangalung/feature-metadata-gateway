"""Dummy feature service and registry."""

from abc import ABC, abstractmethod
from typing import Any


# Abstract base for features
class DummyFeature(ABC):
    """Base class for dummy features."""

    def __init__(self, feature_name: str):
        self.feature_name = feature_name

    @abstractmethod
    def get_feature_values(self, entities: dict[str, list[str]], timestamp: int) -> list[Any]:
        """Get feature values for entities."""
        pass

    @abstractmethod
    def generate_metadata(self, timestamp: int) -> dict[str, Any]:
        """Generate feature metadata."""
        pass

# Abstract interface for service
class FeatureServiceInterface(ABC):
    """Feature service interface."""

    @abstractmethod
    def get_feature_values(self, features: list[str], entities: dict[str, list[str]], timestamp: int) -> dict[str, Any]:
        pass

# Driver conversion rate feature
class DriverConvRateV1(DummyFeature):
    """Driver conversion rate feature."""

    def get_feature_values(self, entities, timestamp):
        driver_ids = entities.get("driver_id", [])
        return [round(hash(d + str(timestamp)) % 100 / 100, 2) for d in driver_ids]

    def generate_metadata(self, timestamp):
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
            "description": "Conversion rate for driver"
        }

# Driver acceptance rate feature
class DriverAccRateV2(DummyFeature):
    """Driver acceptance rate feature."""

    def get_feature_values(self, entities, timestamp):
        driver_ids = entities.get("driver_id", [])
        return [hash(d + str(timestamp)) % 100 + 1 for d in driver_ids]

    def generate_metadata(self, timestamp):
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
            "description": "Acceptance rate for driver"
        }

# Driver average daily trips feature
class DriverAvgTripsV3(DummyFeature):
    """Driver average daily trips feature."""

    def get_feature_values(self, entities, timestamp):
        driver_ids = entities.get("driver_id", [])
        levels = ["Low", "Medium", "High", "Very High"]
        return [levels[hash(d + str(timestamp)) % len(levels)] for d in driver_ids]

    def generate_metadata(self, timestamp):
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
            "description": "Average daily trips"
        }

# Fraud amount feature
class FraudAmountV1(DummyFeature):
    """Fraud amount feature."""

    def get_feature_values(self, entities, timestamp):
        transaction_ids = entities.get("transaction_id", [])
        return [round(hash(t + str(timestamp)) % 10000 / 100, 2) for t in transaction_ids]

    def generate_metadata(self, timestamp):
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
            "description": "Fraud amount for transaction"
        }

# Customer income feature
class CustomerIncomeV1(DummyFeature):
    """Customer income feature."""

    def get_feature_values(self, entities, timestamp):
        customer_ids = entities.get("customer_id", [])
        return [float(20000 + (hash(c + str(timestamp)) % 180001)) for c in customer_ids]

    def generate_metadata(self, timestamp):
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
            "description": "Customer income"
        }

# Registry for features
FEATURE_REGISTRY = {
    "driver_hourly_stats:conv_rate:1": {
        "class": DriverConvRateV1,
        "type": "real-time",
        "description": "Conversion rate for driver"
    },
    "driver_hourly_stats:acc_rate:2": {
        "class": DriverAccRateV2,
        "type": "batch",
        "description": "Acceptance rate for driver"
    },
    "driver_hourly_stats:avg_daily_trips:3": {
        "class": DriverAvgTripsV3,
        "type": "real-time",
        "description": "Average daily trips"
    },
    "fraud:amount:v1": {
        "class": FraudAmountV1,
        "type": "real-time",
        "description": "Fraud amount for transaction"
    },
    "customer:income:v1": {
        "class": CustomerIncomeV1,
        "type": "batch",
        "description": "Customer income"
    }
}

# Dummy feature service
class DummyFeatureService(FeatureServiceInterface):
    """Dummy feature service."""

    def __init__(self):
        self.feature_definitions = {
            k: v["class"](k) for k, v in FEATURE_REGISTRY.items()
        }

    def get_feature_values(self, features, entities, timestamp):
        results = []
        for entity_id in list(entities.values())[0]:
            values = [entity_id]
            messages = []
            event_timestamps = []
            for feature_name in features:
                feature = self.feature_definitions.get(feature_name)
                if feature:
                    val = feature.get_feature_values({list(entities.keys())[0]: [entity_id]}, timestamp)[0]
                    values.append(val)
                    messages.append("200 OK")
                    event_timestamps.append(timestamp)
            results.append({
                "values": values,
                "messages": messages,
                "event_timestamps": event_timestamps
            })
        metadata = {
            "feature_names": [list(entities.keys())[0]] + features
        }
        return {
            "metadata": metadata,
            "results": results
        }

def get_dummy_feature_service():
    return DummyFeatureService()

# For test imports
def test_abstract_interface():
    return True

def test_abstract_feature():
    return True
