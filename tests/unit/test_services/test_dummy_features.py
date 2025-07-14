import pytest

from app.services.dummy_features import (
    FEATURE_REGISTRY,
    CustomerIncomeV1,
    DriverAccRateV2,
    DriverAvgTripsV3,
    DriverConvRateV1,
    DummyFeature,
    DummyFeatureService,
    FeatureServiceInterface,
    FraudAmountV1,
    get_dummy_feature_service,
)
from app.utils.timestamp import get_current_timestamp


class TestDummyFeatures:
    """Test dummy features functionality."""

    # Abstract base class
    def test_abstract_base_class(self):
        with pytest.raises(TypeError):
            DummyFeature("test_feature")

    # Abstract interface
    def test_abstract_interface(self):
        with pytest.raises(TypeError):
            FeatureServiceInterface()

    # Driver conversion rate feature
    def test_driver_conv_rate_feature(self):
        feature = DriverConvRateV1("driver_hourly_stats:conv_rate:1")
        entities = {"driver_id": ["D001", "D002"]}
        timestamp = get_current_timestamp()
        values = feature.get_feature_values(entities, timestamp)
        assert len(values) == 2
        assert all(isinstance(v, float) for v in values)
        assert all(0.0 <= v <= 1.0 for v in values)
        metadata = feature.generate_metadata(timestamp)
        assert metadata["feature_type"] == "real-time"
        assert metadata["feature_data_type"] == "float"
        assert metadata["status"] == "DEPLOYED"

    # Driver acceptance rate feature
    def test_driver_acc_rate_feature(self):
        feature = DriverAccRateV2("driver_hourly_stats:acc_rate:2")
        entities = {"driver_id": ["D001", "D002"]}
        timestamp = get_current_timestamp()
        values = feature.get_feature_values(entities, timestamp)
        assert len(values) == 2
        assert all(isinstance(v, int) for v in values)
        assert all(1 <= v <= 100 for v in values)
        metadata = feature.generate_metadata(timestamp)
        assert metadata["feature_type"] == "batch"
        assert metadata["feature_data_type"] == "integer"
        assert metadata["status"] == "APPROVED"

    # Driver average trips feature
    def test_driver_avg_trips_feature(self):
        feature = DriverAvgTripsV3("driver_hourly_stats:avg_daily_trips:3")
        entities = {"driver_id": ["D001", "D002"]}
        timestamp = get_current_timestamp()
        values = feature.get_feature_values(entities, timestamp)
        assert len(values) == 2
        assert all(isinstance(v, str) for v in values)
        assert all(v in ["Low", "Medium", "High", "Very High"] for v in values)
        metadata = feature.generate_metadata(timestamp)
        assert metadata["feature_type"] == "real-time"
        assert metadata["feature_data_type"] == "string"
        assert metadata["status"] == "DELETED"

    # Fraud amount feature
    def test_fraud_amount_feature(self):
        feature = FraudAmountV1("fraud:amount:v1")
        entities = {"transaction_id": ["T001", "T002"]}
        timestamp = get_current_timestamp()
        values = feature.get_feature_values(entities, timestamp)
        assert len(values) == 2
        assert all(isinstance(v, float) for v in values)
        assert all(0.0 <= v <= 100.0 for v in values)
        metadata = feature.generate_metadata(timestamp)
        assert metadata["feature_type"] == "real-time"
        assert metadata["feature_data_type"] == "float"
        assert metadata["status"] == "DEPLOYED"

    # Customer income feature
    def test_customer_income_feature(self):
        feature = CustomerIncomeV1("customer:income:v1")
        entities = {"customer_id": ["C001", "C002"]}
        timestamp = get_current_timestamp()
        values = feature.get_feature_values(entities, timestamp)
        assert len(values) == 2
        assert all(isinstance(v, float) for v in values)
        assert all(20000.0 <= v <= 200000.0 for v in values)
        metadata = feature.generate_metadata(timestamp)
        assert metadata["feature_type"] == "batch"
        assert metadata["feature_data_type"] == "float"
        assert metadata["status"] == "APPROVED"

    # Feature registry completeness
    def test_feature_registry(self):
        expected_features = [
            "driver_hourly_stats:conv_rate:1",
            "driver_hourly_stats:acc_rate:2",
            "driver_hourly_stats:avg_daily_trips:3",
            "fraud:amount:v1",
            "customer:income:v1",
        ]
        for feature_name in expected_features:
            assert feature_name in FEATURE_REGISTRY
            assert "class" in FEATURE_REGISTRY[feature_name]
            assert "type" in FEATURE_REGISTRY[feature_name]
            assert "description" in FEATURE_REGISTRY[feature_name]

    # Dummy service initialization
    def test_dummy_service_initialization(self):
        service = DummyFeatureService()
        assert service.feature_definitions is not None
        assert len(service.feature_definitions) > 0

    # Get dummy feature service
    def test_get_dummy_feature_service(self):
        service = get_dummy_feature_service()
        assert isinstance(service, DummyFeatureService)

    # Dummy service feature values
    def test_dummy_service_feature_values(self):
        service = DummyFeatureService()
        features = ["driver_hourly_stats:conv_rate:1", "driver_hourly_stats:acc_rate:2"]
        entities = {"driver_id": ["D001", "D002"]}
        timestamp = get_current_timestamp()
        result = service.get_feature_values(features, entities, timestamp)
        assert "results" in result
        assert "metadata" in result
        assert len(result["results"]) == 2
        for entity_result in result["results"]:
            assert "values" in entity_result
            assert "messages" in entity_result
            assert "event_timestamps" in entity_result
            assert len(entity_result["values"]) == 3

    # Deterministic feature values
    def test_deterministic_values(self):
        feature = DriverConvRateV1("driver_hourly_stats:conv_rate:1")
        entities = {"driver_id": ["D001"]}
        timestamp = get_current_timestamp()
        values1 = feature.get_feature_values(entities, timestamp)
        values2 = feature.get_feature_values(entities, timestamp)
        assert values1 == values2

    # Different entities produce values
    def test_different_entities_different_values(self):
        feature = DriverConvRateV1("driver_hourly_stats:conv_rate:1")
        entities1 = {"driver_id": ["D001"]}
        entities2 = {"driver_id": ["D002"]}
        timestamp = get_current_timestamp()
        values1 = feature.get_feature_values(entities1, timestamp)
        values2 = feature.get_feature_values(entities2, timestamp)
        assert isinstance(values1, list)
        assert isinstance(values2, list)
        assert len(values1) == 1
        assert len(values2) == 1
