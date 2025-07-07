import pytest
from fastapi.testclient import TestClient

from app.main import app

# Constants
HTTP_OK = 200
TEST_TIMESTAMP = 1751429485000
ENTITY_COUNT_2 = 2
ENTITY_COUNT_3 = 3
ENTITY_COUNT_4 = 4
ENTITY_COUNT_10 = 10
FLOAT_MIN = 0.1
FLOAT_MAX = 1.0
FLOAT_VALUES = [5, 7, 10000, 85, 250, 15, 42, 99, 150, 500]
STRING_VALUES = ["hello", "world", "feature", "value", "test", "data", "sample", "output"]


class TestComprehensiveFeatures:
    """Comprehensive feature testing"""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = TestClient(app)

    def test_all_feature_types_batch(self):
        """Test all feature types in batch"""
        payload = {
            "features": [
                "driver_hourly_stats:conv_rate:1",  # float, READY FOR TESTING
                "driver_hourly_stats:acc_rate:2",  # integer, APPROVED
                "driver_hourly_stats:avg_daily_trips:3",  # string, None status
            ],
            "entities": {"cust_no": ["X123456", "Y789012", "Z111222"]},
            "event_timestamp": TEST_TIMESTAMP,
        }

        response = self.client.post("/features", json=payload)
        assert response.status_code == HTTP_OK

        data = response.json()

        # Check metadata
        expected_feature_names = [
            "cust_no",
            "driver_hourly_stats:conv_rate:1",
            "driver_hourly_stats:acc_rate:2",
            "driver_hourly_stats:avg_daily_trips:3",
        ]
        assert data["metadata"]["feature_names"] == expected_feature_names

        # Check results for each entity
        assert len(data["results"]) == ENTITY_COUNT_3

        for result in data["results"]:
            assert len(result["values"]) == ENTITY_COUNT_4  # Entity + 3 features
            assert len(result["statuses"]) == ENTITY_COUNT_4
            assert len(result["event_timestamps"]) == ENTITY_COUNT_4

            # All should be successful
            for status in result["statuses"]:
                assert status == "200 OK"

            # Check entity ID is string
            assert isinstance(result["values"][0], str)

            # Check feature values
            for i, feature_value in enumerate(result["values"][1:], 1):
                assert "value" in feature_value
                assert "feature_type" in feature_value
                assert "feature_data_type" in feature_value
                assert "event_timestamp" in feature_value

                # Check data type consistency
                if i == 1:  # conv_rate (float)
                    assert feature_value["feature_data_type"] == "float"
                    assert isinstance(feature_value["value"], float)
                    assert FLOAT_MIN <= feature_value["value"] <= FLOAT_MAX
                elif i == ENTITY_COUNT_2:  # acc_rate (integer)
                    assert feature_value["feature_data_type"] == "integer"
                    assert isinstance(feature_value["value"], int)
                    assert feature_value["value"] in FLOAT_VALUES
                elif i == ENTITY_COUNT_3:  # avg_daily_trips (string)
                    assert feature_value["feature_data_type"] == "string"
                    assert isinstance(feature_value["value"], str)
                    assert feature_value["value"] in STRING_VALUES

    def test_feature_status_variations(self):
        """Test features with different statuses"""
        payload = {
            "features": [
                "driver_hourly_stats:conv_rate:1",  # READY FOR TESTING
                "driver_hourly_stats:acc_rate:2",  # APPROVED
                "fraud:amount:v1",  # DEPLOYED
            ],
            "entities": {"cust_no": ["X123456"]},
        }

        response = self.client.post("/features", json=payload)
        assert response.status_code == HTTP_OK

        data = response.json()
        feature_values = data["results"][0]["values"][1:]

        # Check statuses
        assert feature_values[0]["status"] == "READY FOR TESTING"
        assert feature_values[1]["status"] == "APPROVED"
        assert feature_values[ENTITY_COUNT_2]["status"] == "DEPLOYED"

    def test_large_batch_processing(self):
        """Test large batch processing"""
        # Create large entity list
        entities = {"cust_no": [f"entity_{i}" for i in range(ENTITY_COUNT_10)]}

        payload = {
            "features": ["driver_hourly_stats:conv_rate:1", "driver_hourly_stats:acc_rate:2"],
            "entities": entities,
        }

        response = self.client.post("/features", json=payload)
        assert response.status_code == HTTP_OK

        data = response.json()
        assert len(data["results"]) == ENTITY_COUNT_10

        # Check each result
        for result in data["results"]:
            assert len(result["values"]) == ENTITY_COUNT_3  # Entity + 2 features
            assert len(result["statuses"]) == ENTITY_COUNT_3
            assert all(status == "200 OK" for status in result["statuses"])

    def test_deterministic_values_across_requests(self):
        """Test values are deterministic across multiple requests"""
        payload = {
            "features": ["driver_hourly_stats:conv_rate:1"],
            "entities": {"cust_no": ["X123456"]},
            "event_timestamp": TEST_TIMESTAMP,
        }

        # Make multiple requests
        responses = []
        for _ in range(5):
            response = self.client.post("/features", json=payload)
            assert response.status_code == HTTP_OK
            responses.append(response.json())

        # All responses should have same value
        first_value = responses[0]["results"][0]["values"][1]["value"]
        for response_data in responses[1:]:
            current_value = response_data["results"][0]["values"][1]["value"]
            assert current_value == first_value

    def test_different_entities_different_values(self):
        """Test different entities produce different values"""
        payload = {
            "features": ["driver_hourly_stats:conv_rate:1"],
            "entities": {
                "cust_no": [
                    "entity_alpha",
                    "entity_beta",
                    "entity_gamma",
                    "entity_delta",
                    "entity_epsilon",
                    "X999999",
                    "Y888888",
                ]
            },
        }

        response = self.client.post("/features", json=payload)
        assert response.status_code == HTTP_OK

        data = response.json()
        values = []
        for result in data["results"]:
            values.append(result["values"][1]["value"])

        # Should have at least some different values
        unique_values = set(values)
        assert len(unique_values) > 1, f"Expected different values but got: {values}"

    def test_mixed_valid_invalid_features(self):
        """Test mix of valid and invalid features"""
        payload = {
            "features": [
                "driver_hourly_stats:conv_rate:1",  # Valid
                "invalid:feature:format",  # Invalid format but valid structure
                "not_valid_format",  # Invalid format
                "driver_hourly_stats:acc_rate:2",  # Valid
            ],
            "entities": {"cust_no": ["X123456"]},
        }

        response = self.client.post("/features", json=payload)
        assert response.status_code == HTTP_OK

        data = response.json()
        result = data["results"][0]

        # Check statuses: entity + 4 features
        expected_statuses = [
            "200 OK",  # Entity
            "200 OK",  # Valid feature 1
            "404 Not Found",  # Invalid feature 1
            "404 Not Found",  # Invalid feature 2
            "200 OK",  # Valid feature 2
        ]
        assert result["statuses"] == expected_statuses

    def test_feature_metadata_completeness(self):
        """Test all feature metadata fields are present"""
        payload = {
            "features": ["driver_hourly_stats:conv_rate:1"],
            "entities": {"cust_no": ["X123456"]},
        }

        response = self.client.post("/features", json=payload)
        assert response.status_code == HTTP_OK

        feature_value = response.json()["results"][0]["values"][1]

        # Required fields
        required_fields = [
            "value",
            "feature_type",
            "feature_data_type",
            "query",
            "created_time",
            "updated_time",
            "created_by",
            "last_updated_by",
            "event_timestamp",
        ]

        for field in required_fields:
            assert field in feature_value, f"Missing required field: {field}"

        # Optional fields should be present but may be None
        optional_fields = ["approved_by", "status", "description"]
        for field in optional_fields:
            assert field in feature_value, f"Missing optional field: {field}"

    def test_timestamp_propagation(self):
        """Test timestamp propagation through system"""
        test_timestamp = TEST_TIMESTAMP

        payload = {
            "features": ["driver_hourly_stats:conv_rate:1"],
            "entities": {"cust_no": ["X123456"]},
            "event_timestamp": test_timestamp,
        }

        response = self.client.post("/features", json=payload)
        assert response.status_code == HTTP_OK

        data = response.json()
        result = data["results"][0]

        # Check all timestamps match
        for timestamp in result["event_timestamps"]:
            assert timestamp == test_timestamp

        # Check feature metadata timestamp
        feature_value = result["values"][1]
        assert feature_value["event_timestamp"] == test_timestamp

    def test_error_handling_edge_cases(self):
        """Test error handling edge cases"""
        # Empty features and entities
        payload = {
            "features": [],
            "entities": {"cust_no": []},
        }

        response = self.client.post("/features", json=payload)
        assert response.status_code == HTTP_OK

        data = response.json()
        assert data["metadata"]["feature_names"] == ["cust_no"]
        assert len(data["results"]) == 0

    def test_feature_type_combinations(self):
        """Test different feature type combinations"""
        payload = {
            "features": [
                "driver_hourly_stats:conv_rate:1",  # real-time, float
                "driver_hourly_stats:acc_rate:2",  # batch, integer
            ],
            "entities": {"cust_no": ["X123456"]},
        }

        response = self.client.post("/features", json=payload)
        assert response.status_code == HTTP_OK

        data = response.json()
        feature_values = data["results"][0]["values"][1:]

        # Check feature types
        assert feature_values[0]["feature_type"] == "real-time"
        assert feature_values[1]["feature_type"] == "batch"

        # Check data types match values
        assert feature_values[0]["feature_data_type"] == "float"
        assert isinstance(feature_values[0]["value"], float)

        assert feature_values[1]["feature_data_type"] == "integer"
        assert isinstance(feature_values[1]["value"], int)
