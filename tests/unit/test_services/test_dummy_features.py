import pytest

from app.services.dummy_features import (
    FEATURE_METADATA_REGISTRY,
    CustomerIncomeV1,
    DriverAccRateV2,
    DriverAvgTripsV3,
    DriverConvRateV1,
    DummyFeatureMetadata,
    FraudAmountV1,
)
from app.utils.timestamp import get_current_timestamp


class TestDummyFeatures:
    def test_abstract_base(self):
        with pytest.raises(TypeError):
            DummyFeatureMetadata("test_feature")

    def test_driver_conv_rate(self):
        feature = DriverConvRateV1("driver_hourly_stats:conv_rate:1")
        timestamp = get_current_timestamp()
        values = feature.generate_metadata(timestamp)
        assert values["feature_type"] == "real-time"
        assert values["feature_data_type"] == "float"
        assert values["status"] == "DEPLOYED"

    def test_driver_acc_rate(self):
        feature = DriverAccRateV2("driver_hourly_stats:acc_rate:2")
        timestamp = get_current_timestamp()
        values = feature.generate_metadata(timestamp)
        assert values["feature_type"] == "batch"
        assert values["feature_data_type"] == "integer"
        assert values["status"] == "APPROVED"

    def test_driver_avg_trips(self):
        feature = DriverAvgTripsV3("driver_hourly_stats:avg_daily_trips:3")
        timestamp = get_current_timestamp()
        values = feature.generate_metadata(timestamp)
        assert values["feature_type"] == "real-time"
        assert values["feature_data_type"] == "string"
        assert values["status"] == "DELETED"

    def test_fraud_amount(self):
        feature = FraudAmountV1("fraud:amount:v1")
        timestamp = get_current_timestamp()
        values = feature.generate_metadata(timestamp)
        assert values["feature_type"] == "real-time"
        assert values["feature_data_type"] == "float"
        assert values["status"] == "DEPLOYED"

    def test_customer_income(self):
        feature = CustomerIncomeV1("customer:income:v1")
        timestamp = get_current_timestamp()
        values = feature.generate_metadata(timestamp)
        assert values["feature_type"] == "batch"
        assert values["feature_data_type"] == "float"
        assert values["status"] == "APPROVED"

    def test_registry(self):
        expected = [
            "driver_hourly_stats:conv_rate:1",
            "driver_hourly_stats:acc_rate:2",
            "driver_hourly_stats:avg_daily_trips:3",
            "fraud:amount:v1",
            "customer:income:v1",
        ]
        for name in expected:
            assert name in FEATURE_METADATA_REGISTRY
            assert "class" in FEATURE_METADATA_REGISTRY[name]
            assert "type" in FEATURE_METADATA_REGISTRY[name]
            assert "description" in FEATURE_METADATA_REGISTRY[name]
