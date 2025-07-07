import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.main import app
from app.models.request import FeatureRequest
from app.services.dummy_features import FEATURE_REGISTRY
from app.utils.timestamp import get_current_timestamp_ms

# Test constants
HTTP_OK = 200
HTTP_UNPROCESSABLE_ENTITY = 422
ENTITY_COUNT_4 = 4
TEST_TIMESTAMP = 1751429485000


class TestValidation:
    """Request validation test suite"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test client"""
        self.client = TestClient(app)
        self.available_features = list(FEATURE_REGISTRY.keys())

    @pytest.mark.parametrize(
        "features,should_succeed",
        [
            # Valid feature formats
            (["driver_hourly_stats:conv_rate:1"], True),
            (["driver_hourly_stats:acc_rate:2"], True),
            (["driver_hourly_stats:conv_rate:1", "driver_hourly_stats:acc_rate:2"], True),
            # Non-existent feature
            (["unknown:feature:version"], False),
            # Invalid feature formats
            (["driver:hourly:stats:conv"], False),
            (["driver_hourly_stats"], False),
            ([":conv_rate:1"], False),
            (["driver_hourly_stats:"], False),
            ([""], False),
            # Mixed valid/invalid formats
            (["driver_hourly_stats:conv_rate:1", "invalid:format:here:extra"], False),
        ],
    )
    def test_feature_format_validation(self, features, should_succeed):
        """Test feature format validation"""
        payload = {
            "features": features,
            "entities": {"cust_no": ["X123456"]},
            "event_timestamp": get_current_timestamp_ms(),
        }
        response = self.client.post("/features", json=payload)
        assert response.status_code == HTTP_OK

        if features:
            data = response.json()
            result = data["results"][0]

            if should_succeed:
                # All features return success
                feature_statuses = result["statuses"][1:]
                for status in feature_statuses:
                    assert status == "200 OK"
            else:
                # At least one failure
                feature_statuses = result["statuses"][1:]
                has_failure = any(
                    "404 Not Found" in status or "500" in status for status in feature_statuses
                )
                assert has_failure, f"Expected failure but got statuses: {feature_statuses}"

    @pytest.mark.parametrize(
        "entities,expected_status",
        [
            # Valid entity configurations
            ({"cust_no": ["X123456"]}, HTTP_OK),
            ({"cust_no": ["123456"]}, HTTP_OK),
            ({"cust_no": ["X123456", "1002"]}, HTTP_OK),
            # Edge cases
            ({"cust_no": []}, HTTP_OK),
            ({}, HTTP_UNPROCESSABLE_ENTITY),
        ],
    )
    def test_entity_validation(self, entities, expected_status):
        """Test entity validation rules"""
        payload = {
            "features": ["driver_hourly_stats:conv_rate:1"],
            "entities": entities,
            "event_timestamp": get_current_timestamp_ms(),
        }
        response = self.client.post("/features", json=payload)
        assert response.status_code == expected_status

    def test_request_validation_coverage(self):
        """Test request validation edge cases"""
        # Invalid features type
        with pytest.raises((ValidationError, TypeError)):
            FeatureRequest(features="not_a_list", entities={"cust_no": ["X123456"]})

        # Invalid entities type
        with pytest.raises((ValidationError, TypeError)):
            FeatureRequest(features=["driver_hourly_stats:conv_rate:1"], entities="not_a_dict")

        # Empty entities dictionary
        with pytest.raises(ValidationError):
            FeatureRequest(features=["driver_hourly_stats:conv_rate:1"], entities={})

    def test_timestamp_handling(self):
        """Test timestamp handling behavior"""
        # Request without timestamp
        payload = {
            "features": ["driver_hourly_stats:conv_rate:1"],
            "entities": {"cust_no": ["X123456"]},
        }
        response = self.client.post("/features", json=payload)
        assert response.status_code == HTTP_OK

        # Request with timestamp
        payload = {
            "features": ["driver_hourly_stats:conv_rate:1"],
            "entities": {"cust_no": ["X123456"]},
            "event_timestamp": TEST_TIMESTAMP,
        }
        response = self.client.post("/features", json=payload)
        assert response.status_code == HTTP_OK

        data = response.json()
        feature_value = data["results"][0]["values"][1]
        assert feature_value["event_timestamp"] == TEST_TIMESTAMP

    def test_multiple_entity_types(self):
        """Test multiple entity types"""
        payload = {
            "features": ["driver_hourly_stats:conv_rate:1"],
            "entities": {"cust_no": ["X123456", "Y789012"], "driver_id": ["D001", "D002"]},
        }
        response = self.client.post("/features", json=payload)
        assert response.status_code == HTTP_OK

        data = response.json()
        assert len(data["results"]) == ENTITY_COUNT_4

    def test_feature_value_data_type_consistency(self):
        """Test feature data type consistency"""
        payload = {
            "features": [
                "driver_hourly_stats:conv_rate:1",  # float
                "driver_hourly_stats:acc_rate:2",  # integer
                "driver_hourly_stats:avg_daily_trips:3",  # string
            ],
            "entities": {"cust_no": ["X123456"]},
        }
        response = self.client.post("/features", json=payload)
        assert response.status_code == HTTP_OK

        data = response.json()
        feature_values = data["results"][0]["values"][1:]

        # Verify float feature
        float_feature = feature_values[0]
        assert float_feature["feature_data_type"] == "float"
        assert isinstance(float_feature["value"], float)

        # Verify integer feature
        int_feature = feature_values[1]
        assert int_feature["feature_data_type"] == "integer"
        assert isinstance(int_feature["value"], int)

        # Verify string feature
        str_feature = feature_values[2]
        assert str_feature["feature_data_type"] == "string"
        assert isinstance(str_feature["value"], str)

    def test_empty_features_with_entities(self):
        """Test empty features with entities"""
        payload = {
            "features": [],
            "entities": {"cust_no": ["X123456"]},
        }
        response = self.client.post("/features", json=payload)
        assert response.status_code == HTTP_OK

        data = response.json()
        assert len(data["results"]) == 1
        assert len(data["results"][0]["values"]) == 1
