import pytest
from fastapi.testclient import TestClient

from app.main import app

# Test constants
HTTP_OK = 200
TEST_TIMESTAMP = 1751429485000
ENTITY_COUNT_2 = 2
ENTITY_COUNT_3 = 3
ENTITY_COUNT_4 = 4
ENTITY_COUNT_10 = 10


class TestComprehensiveFeatures:
    """Comprehensive feature test suite"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test client"""
        self.client = TestClient(app)

    def test_exact_response_format(self):
        """Test exact response format match"""
        payload = {
            "features": ["driver_hourly_stats:conv_rate:1", "driver_hourly_stats:acc_rate:2"],
            "entities": {"cust_no": ["X123456", "1002"]},
            "event_timestamp": TEST_TIMESTAMP,
        }

        response = self.client.post("/features", json=payload)
        assert response.status_code == HTTP_OK

        data = response.json()

        # Verify metadata structure
        assert data["metadata"]["feature_names"] == [
            "cust_no",
            "driver_hourly_stats:conv_rate:1",
            "driver_hourly_stats:acc_rate:2"
        ]

        # Verify results structure
        assert len(data["results"]) == ENTITY_COUNT_2

        # Check first entity result
        first_result = data["results"][0]
        assert first_result["values"][0] == "X123456"
        assert len(first_result["values"]) == ENTITY_COUNT_3
        assert len(first_result["statuses"]) == ENTITY_COUNT_3
        assert len(first_result["event_timestamps"]) == ENTITY_COUNT_3

        # Check second entity result
        second_result = data["results"][1]
        assert second_result["values"][0] == "1002"
        assert len(second_result["values"]) == ENTITY_COUNT_3

        # Verify feature value structure
        conv_rate_feature = first_result["values"][1]
        assert isinstance(conv_rate_feature["value"], float)
        assert conv_rate_feature["feature_type"] == "real-time"
        assert conv_rate_feature["feature_data_type"] == "float"
        assert "query" in conv_rate_feature

        acc_rate_feature = first_result["values"][2]
        assert isinstance(acc_rate_feature["value"], int)
        assert acc_rate_feature["feature_type"] == "batch"
        assert acc_rate_feature["feature_data_type"] == "integer"

    def test_deterministic_values_per_entity(self):
        """Test deterministic values per entity"""
        payload = {
            "features": ["driver_hourly_stats:conv_rate:1"],
            "entities": {"cust_no": ["X123456", "1002"]},
            "event_timestamp": TEST_TIMESTAMP,
        }

        response = self.client.post("/features", json=payload)
        assert response.status_code == HTTP_OK

        data = response.json()

        # Values should be different for different entities
        first_value = data["results"][0]["values"][1]["value"]
        second_value = data["results"][1]["values"][1]["value"]

        # Same feature, different entities = different values
        assert first_value != second_value

        # Consistency check - same request should return same values
        response2 = self.client.post("/features", json=payload)
        data2 = response2.json()

        assert data2["results"][0]["values"][1]["value"] == first_value
        assert data2["results"][1]["values"][1]["value"] == second_value

    def test_all_feature_types_batch(self):
        """Test all feature types"""
        payload = {
            "features": [
                "driver_hourly_stats:conv_rate:1",  # float
                "driver_hourly_stats:acc_rate:2",   # integer
                "driver_hourly_stats:avg_daily_trips:3"  # string
            ],
            "entities": {"cust_no": ["X123456", "Y789012"]},
            "event_timestamp": TEST_TIMESTAMP,
        }

        response = self.client.post("/features", json=payload)
        assert response.status_code == HTTP_OK

        data = response.json()

        # Check metadata includes all features
        expected_feature_names = [
            "cust_no",
            "driver_hourly_stats:conv_rate:1",
            "driver_hourly_stats:acc_rate:2",
            "driver_hourly_stats:avg_daily_trips:3",
        ]
        assert data["metadata"]["feature_names"] == expected_feature_names

        # Check each entity result
        assert len(data["results"]) == ENTITY_COUNT_2
        for result in data["results"]:
            assert len(result["values"]) == ENTITY_COUNT_4  # Entity + 3 features
            assert len(result["statuses"]) == ENTITY_COUNT_4

            # Verify data types
            conv_rate_val = result["values"][1]
            assert isinstance(conv_rate_val["value"], float)
            assert conv_rate_val["feature_data_type"] == "float"

            acc_rate_val = result["values"][2]
            assert isinstance(acc_rate_val["value"], int)
            assert acc_rate_val["feature_data_type"] == "integer"

            avg_trips_val = result["values"][3]
            assert isinstance(avg_trips_val["value"], str)
            assert avg_trips_val["feature_data_type"] == "string"

    def test_large_batch_processing(self):
        """Test large batch processing"""
        entities = {"cust_no": [f"entity_{i}" for i in range(ENTITY_COUNT_10)]}

        payload = {
            "features": ["driver_hourly_stats:conv_rate:1", "driver_hourly_stats:acc_rate:2"],
            "entities": entities,
        }

        response = self.client.post("/features", json=payload)
        assert response.status_code == HTTP_OK

        data = response.json()
        assert len(data["results"]) == ENTITY_COUNT_10

        # Check each result structure
        for i, result in enumerate(data["results"]):
            assert result["values"][0] == f"entity_{i}"  # Entity ID
            assert len(result["values"]) == ENTITY_COUNT_3  # Entity + 2 features
            assert len(result["statuses"]) == ENTITY_COUNT_3
            assert all(status == "200 OK" for status in result["statuses"])

    def test_mixed_valid_invalid_features(self):
        """Test mixed valid/invalid features"""
        payload = {
            "features": [
                "driver_hourly_stats:conv_rate:1",  # Valid
                "invalid:feature:format",          # Invalid
                "driver_hourly_stats:acc_rate:2",  # Valid
            ],
            "entities": {"cust_no": ["X123456"]},
        }

        response = self.client.post("/features", json=payload)
        assert response.status_code == HTTP_OK

        data = response.json()
        result = data["results"][0]

        # Check statuses: entity + 3 features
        expected_statuses = [
            "200 OK",         # Entity
            "200 OK",         # Valid feature 1
            "404 Not Found",  # Invalid feature
            "200 OK",         # Valid feature 2
        ]
        assert result["statuses"] == expected_statuses

        # Check that invalid feature has error placeholder
        invalid_feature = result["values"][2]
        assert invalid_feature["value"] is None
        assert invalid_feature["status"] == "NOT_FOUND"

    def test_empty_features_list(self):
        """Test empty features list"""
        payload = {
            "features": [],
            "entities": {"cust_no": ["X123456"]},
        }

        response = self.client.post("/features", json=payload)
        assert response.status_code == HTTP_OK

        data = response.json()
        assert len(data["results"]) == 1
        assert len(data["results"][0]["values"]) == 1  # Only entity ID
        assert data["results"][0]["values"][0] == "X123456"

    def test_multiple_entity_types(self):
        """Test multiple entity types"""
        payload = {
            "features": ["driver_hourly_stats:conv_rate:1"],
            "entities": {
                "cust_no": ["X123456", "Y789012"],
                "driver_id": ["D001", "D002"]
            },
        }

        response = self.client.post("/features", json=payload)
        assert response.status_code == HTTP_OK

        data = response.json()
        # Should have 4 results (2 cust_no + 2 driver_id)
        assert len(data["results"]) == ENTITY_COUNT_4

        # Check entity IDs are correct
        entity_values = [result["values"][0] for result in data["results"]]
        assert "X123456" in entity_values
        assert "Y789012" in entity_values
        assert "D001" in entity_values
        assert "D002" in entity_values
