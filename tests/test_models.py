import pytest
from pydantic import ValidationError

from app.models.request import FeatureRequest
from app.models.response import EntityResult, FeatureResponse, FeatureValue

# Test constants
TEST_FLOAT_VALUE = 0.75
TEST_TIMESTAMP = 1751429485000
ENTITY_COUNT_2 = 2


class TestRequestModels:
    """Request model test suite"""

    def test_valid_request(self):
        """Test valid request creation"""
        request = FeatureRequest(
            features=["driver_hourly_stats:conv_rate:1"],
            entities={"cust_no": ["X123456"]},
            event_timestamp=TEST_TIMESTAMP,
        )

        assert len(request.features) == 1
        assert "cust_no" in request.entities
        assert request.event_timestamp == TEST_TIMESTAMP

    def test_invalid_features_type(self):
        """Test invalid features type"""
        with pytest.raises((ValidationError, TypeError)):
            FeatureRequest(features="not_a_list", entities={"cust_no": ["X123456"]})

    def test_empty_entities(self):
        """Test empty entities validation"""
        with pytest.raises(ValidationError):
            FeatureRequest(features=["driver_hourly_stats:conv_rate:1"], entities={})

    def test_optional_timestamp(self):
        """Test optional timestamp handling"""
        request = FeatureRequest(
            features=["driver_hourly_stats:conv_rate:1"], entities={"cust_no": ["X123456"]}
        )

        assert request.event_timestamp is None

    def test_features_not_list_validation(self):
        """Test features type validation"""
        with pytest.raises((ValidationError, TypeError)) as exc_info:
            FeatureRequest(features={"not": "a_list"}, entities={"cust_no": ["X123456"]})
        error_str = str(exc_info.value)
        assert "features must be a list" in error_str or "list" in error_str.lower()

    def test_entities_not_dict_validation(self):
        """Test entities type validation"""
        with pytest.raises((ValidationError, TypeError)) as exc_info:
            FeatureRequest(
                features=["driver_hourly_stats:conv_rate:1"], entities=["not", "a", "dict"]
            )
        error_str = str(exc_info.value)
        assert "entities must be a dictionary" in error_str or "dict" in error_str.lower()


class TestResponseModels:
    """Response model test suite"""

    def test_feature_value_model(self):
        """Test feature value creation"""
        feature_value = FeatureValue(
            value=TEST_FLOAT_VALUE,
            feature_type="real-time",
            feature_data_type="float",
            query="SELECT * FROM table",
            created_time=TEST_TIMESTAMP,
            updated_time=TEST_TIMESTAMP,
            created_by="user1",
            last_updated_by="user2",
            approved_by="approver",
            status="READY FOR TESTING",
            description="Test feature",
            event_timestamp=TEST_TIMESTAMP,
        )

        assert feature_value.value == TEST_FLOAT_VALUE
        assert feature_value.feature_type == "real-time"
        assert feature_value.status == "READY FOR TESTING"

    def test_entity_result_model(self):
        """Test entity result creation"""
        feature_value = FeatureValue(
            value=TEST_FLOAT_VALUE,
            feature_type="real-time",
            feature_data_type="float",
            query="SELECT * FROM table",
            created_time=TEST_TIMESTAMP,
            updated_time=TEST_TIMESTAMP,
            created_by="user1",
            last_updated_by="user2",
            event_timestamp=TEST_TIMESTAMP,
        )

        entity_result = EntityResult(
            values=["X123456", feature_value],
            statuses=["200 OK", "200 OK"],
            event_timestamps=[TEST_TIMESTAMP, TEST_TIMESTAMP],
        )

        assert len(entity_result.values) == ENTITY_COUNT_2
        assert entity_result.values[0] == "X123456"
        assert isinstance(entity_result.values[1], FeatureValue)

    def test_feature_response_model(self):
        """Test feature response creation"""
        feature_value = FeatureValue(
            value=TEST_FLOAT_VALUE,
            feature_type="real-time",
            feature_data_type="float",
            query="SELECT * FROM table",
            created_time=TEST_TIMESTAMP,
            updated_time=TEST_TIMESTAMP,
            created_by="user1",
            last_updated_by="user2",
            event_timestamp=TEST_TIMESTAMP,
        )

        entity_result = EntityResult(
            values=["X123456", feature_value],
            statuses=["200 OK", "200 OK"],
            event_timestamps=[TEST_TIMESTAMP, TEST_TIMESTAMP],
        )

        response = FeatureResponse(
            metadata={"feature_names": ["cust_no", "driver_hourly_stats:conv_rate:1"]},
            results=[entity_result],
        )

        assert "feature_names" in response.metadata
        assert len(response.results) == 1
