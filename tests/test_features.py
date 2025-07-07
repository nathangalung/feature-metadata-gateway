import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.dummy_features import FEATURE_REGISTRY
from app.utils.timestamp import get_current_timestamp_ms

# Constants
HTTP_OK = 200
ENTITY_COUNT_3 = 3


class TestFeatures:
    """Feature functionality tests"""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = TestClient(app)
        self.available_features = list(FEATURE_REGISTRY.keys())

    def test_feature_consistency(self):
        """Feature consistency"""
        payload = {
            "features": ["driver_hourly_stats:conv_rate:1"],
            "entities": {"cust_no": ["X123456"]},
            "event_timestamp": 1751429485000,
        }

        responses = []
        for _ in range(3):
            response = self.client.post("/features", json=payload)
            assert response.status_code == HTTP_OK
            responses.append(response.json())

        # Check consistency
        for i in range(1, len(responses)):
            first_value = responses[0]["results"][0]["values"][1]["value"]
            current_value = responses[i]["results"][0]["values"][1]["value"]
            assert current_value == first_value

    def test_feature_status_hierarchy(self):
        """Feature status hierarchy"""
        # Test different features with different statuses
        payload = {
            "features": [
                "driver_hourly_stats:conv_rate:1",  # READY FOR TESTING
                "driver_hourly_stats:acc_rate:2",  # APPROVED
                "fraud:amount:v1",  # DEPLOYED
            ],
            "entities": {"cust_no": ["X123456"]},
            "event_timestamp": get_current_timestamp_ms(),
        }

        response = self.client.post("/features", json=payload)
        assert response.status_code == HTTP_OK

        data = response.json()
        result = data["results"][0]

        # Check that all features return successfully
        for i, status in enumerate(result["statuses"]):
            if i == 0:  # Entity ID
                assert status == "200 OK"
            else:  # Features
                assert status == "200 OK"

    def test_feature_data_types(self):
        """Feature data types"""
        payload = {
            "features": [
                "driver_hourly_stats:conv_rate:1",  # float
                "driver_hourly_stats:acc_rate:2",  # integer
                "driver_hourly_stats:avg_daily_trips:3",  # string
            ],
            "entities": {"cust_no": ["X123456"]},
            "event_timestamp": get_current_timestamp_ms(),
        }

        response = self.client.post("/features", json=payload)
        assert response.status_code == HTTP_OK

        data = response.json()
        feature_values = data["results"][0]["values"][1:]  # Skip entity ID

        # Check data types
        assert feature_values[0]["feature_data_type"] == "float"
        assert isinstance(feature_values[0]["value"], float)

        assert feature_values[1]["feature_data_type"] == "integer"
        assert isinstance(feature_values[1]["value"], int)

        assert feature_values[2]["feature_data_type"] == "string"
        assert isinstance(feature_values[2]["value"], str)

    def test_batch_processing(self):
        """Batch processing"""
        payload = {
            "features": ["driver_hourly_stats:conv_rate:1", "driver_hourly_stats:acc_rate:2"],
            "entities": {"cust_no": ["X123456", "1002", "1003"]},
            "event_timestamp": get_current_timestamp_ms(),
        }

        response = self.client.post("/features", json=payload)
        assert response.status_code == HTTP_OK

        data = response.json()
        assert len(data["results"]) == ENTITY_COUNT_3  # 3 entities

        for result in data["results"]:
            assert len(result["values"]) == ENTITY_COUNT_3  # Entity ID + 2 features
            assert len(result["statuses"]) == ENTITY_COUNT_3
            assert len(result["event_timestamps"]) == ENTITY_COUNT_3

    def test_unknown_features(self):
        """Unknown features handling"""
        payload = {
            "features": [
                "driver_hourly_stats:conv_rate:1",  # Known
                "unknown:feature:1",  # Unknown
            ],
            "entities": {"cust_no": ["X123456"]},
            "event_timestamp": get_current_timestamp_ms(),
        }

        response = self.client.post("/features", json=payload)
        assert response.status_code == HTTP_OK

        data = response.json()
        result = data["results"][0]

        # First feature should succeed, second should fail
        assert result["statuses"][0] == "200 OK"  # Entity ID
        assert result["statuses"][1] == "200 OK"  # Known feature
        assert result["statuses"][2] == "404 Not Found"  # Unknown feature

    def test_empty_features_list(self):
        """Empty features list"""
        payload = {
            "features": [],
            "entities": {"cust_no": ["X123456"]},
            "event_timestamp": get_current_timestamp_ms(),
        }

        response = self.client.post("/features", json=payload)
        assert response.status_code == HTTP_OK

        data = response.json()
        assert len(data["results"]) == 1
        result = data["results"][0]
        assert len(result["values"]) == 1  # Only entity ID
        assert result["values"][0] == "X123456"

    def test_empty_entities_list(self):
        """Empty entities list"""
        payload = {
            "features": ["driver_hourly_stats:conv_rate:1"],
            "entities": {"cust_no": []},
            "event_timestamp": get_current_timestamp_ms(),
        }

        response = self.client.post("/features", json=payload)
        assert response.status_code == HTTP_OK

        data = response.json()
        assert len(data["results"]) == 0
