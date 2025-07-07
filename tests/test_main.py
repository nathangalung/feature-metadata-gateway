from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.main import app
from app.utils.timestamp import get_current_timestamp_ms

# Test constants
HTTP_OK = 200
HTTP_UNPROCESSABLE_ENTITY = 422
HTTP_INTERNAL_SERVER_ERROR = 500
ENTITY_COUNT_2 = 2
ENTITY_COUNT_3 = 3
ENTITY_COUNT_4 = 4


class TestMain:
    """Main functionality test suite"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test client"""
        self.client = TestClient(app)

    def test_health_check(self):
        """Test health endpoint"""
        response = self.client.get("/health")
        assert response.status_code == HTTP_OK
        data = response.json()
        assert data["status"] == "ok"
        assert "timestamp" in data

    def test_invalid_request_format(self):
        """Test invalid request format"""
        response = self.client.post(
            "/features",
            headers={"Content-Type": "application/json"},
            content='{"invalid": "format"}',
        )
        assert response.status_code == HTTP_UNPROCESSABLE_ENTITY

    def test_malformed_json(self):
        """Test malformed JSON handling"""
        response = self.client.post(
            "/features",
            headers={"Content-Type": "application/json"},
            content='{"features": ["test"], "entities": {',
        )
        assert response.status_code == HTTP_UNPROCESSABLE_ENTITY

    def test_server_error_simulation(self):
        """Test server error handling"""
        payload = {
            "features": ["driver_hourly_stats:conv_rate:1"],
            "entities": {"cust_no": ["X123456"]},
            "event_timestamp": "not_a_number",
        }
        response = self.client.post("/features", json=payload)
        assert response.status_code == HTTP_UNPROCESSABLE_ENTITY

    def test_feature_service_exception_handling(self):
        """Test service exception coverage"""
        # Mock service to raise exception
        with patch("app.main.feature_service") as mock_service:
            mock_service.batch_process_features = AsyncMock(side_effect=Exception("Service error"))

            payload = {
                "features": ["driver_hourly_stats:conv_rate:1"],
                "entities": {"cust_no": ["X123456"]},
                "event_timestamp": get_current_timestamp_ms(),
            }

            response = self.client.post("/features", json=payload)
            assert response.status_code == HTTP_INTERNAL_SERVER_ERROR

    def test_pydantic_validation_error_handling(self):
        """Test Pydantic validation error coverage"""
        # Mock EntityResult to raise ValidationError
        with patch("app.main.EntityResult") as mock_entity_result:
            mock_entity_result.side_effect = ValidationError.from_exception_data(
                "ValidationError",
                [{"type": "string_type", "loc": ("values", 1), "msg": "Input should be valid"}],
            )

            payload = {
                "features": ["driver_hourly_stats:conv_rate:1"],
                "entities": {"cust_no": ["X123456"]},
            }

            response = self.client.post("/features", json=payload)
            assert response.status_code == HTTP_INTERNAL_SERVER_ERROR


class TestFeatureEndpoint:
    """Feature endpoint test suite"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test client"""
        self.client = TestClient(app)

    def test_single_feature_single_entity(self):
        """Test single feature request"""
        payload = {
            "features": ["driver_hourly_stats:conv_rate:1"],
            "entities": {"cust_no": ["X123456"]},
            "event_timestamp": get_current_timestamp_ms(),
        }

        response = self.client.post("/features", json=payload)
        assert response.status_code == HTTP_OK

        data = response.json()
        assert "metadata" in data
        assert "results" in data
        assert len(data["results"]) == 1

        result = data["results"][0]
        assert len(result["values"]) == ENTITY_COUNT_2
        assert result["values"][0] == "X123456"
        assert isinstance(result["values"][1], dict)
        assert "value" in result["values"][1]

    def test_multiple_features_multiple_entities(self):
        """Test multiple features request"""
        payload = {
            "features": ["driver_hourly_stats:conv_rate:1", "driver_hourly_stats:acc_rate:2"],
            "entities": {"cust_no": ["X123456", "1002"]},
            "event_timestamp": get_current_timestamp_ms(),
        }

        response = self.client.post("/features", json=payload)
        assert response.status_code == HTTP_OK

        data = response.json()
        assert len(data["results"]) == ENTITY_COUNT_2

        for result in data["results"]:
            assert len(result["values"]) == ENTITY_COUNT_3
            assert len(result["statuses"]) == ENTITY_COUNT_3
            assert len(result["event_timestamps"]) == ENTITY_COUNT_3

    def test_metadata_structure(self):
        """Test response metadata structure"""
        payload = {
            "features": ["driver_hourly_stats:conv_rate:1"],
            "entities": {"cust_no": ["X123456"]},
            "event_timestamp": get_current_timestamp_ms(),
        }

        response = self.client.post("/features", json=payload)
        assert response.status_code == HTTP_OK

        data = response.json()
        metadata = data["metadata"]
        assert "feature_names" in metadata
        assert "cust_no" in metadata["feature_names"]
        assert "driver_hourly_stats:conv_rate:1" in metadata["feature_names"]

    def test_feature_value_structure(self):
        """Test feature value structure"""
        payload = {
            "features": ["driver_hourly_stats:conv_rate:1"],
            "entities": {"cust_no": ["X123456"]},
            "event_timestamp": get_current_timestamp_ms(),
        }

        response = self.client.post("/features", json=payload)
        assert response.status_code == HTTP_OK

        feature_value = response.json()["results"][0]["values"][1]
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
            assert field in feature_value

    def test_available_features(self):
        """Test available features endpoint"""
        response = self.client.get("/features/available")
        assert response.status_code == HTTP_OK

        data = response.json()
        assert "available_features" in data
        assert len(data["available_features"]) > 0
        assert "driver_hourly_stats:conv_rate:1" in data["available_features"]


class TestIntegration:
    """Integration test suite"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test client"""
        self.client = TestClient(app)

    def test_response_structure(self):
        """Test complete response structure"""
        payload = {
            "features": [
                "driver_hourly_stats:conv_rate:1",
                "driver_hourly_stats:acc_rate:2",
                "driver_hourly_stats:avg_daily_trips:3",
            ],
            "entities": {"cust_no": ["X123456", "1002"]},
            "event_timestamp": 1751429485000,
        }

        response = self.client.post("/features", json=payload)
        assert response.status_code == HTTP_OK

        data = response.json()

        # Verify metadata structure
        assert data["metadata"]["feature_names"] == [
            "cust_no",
            "driver_hourly_stats:conv_rate:1",
            "driver_hourly_stats:acc_rate:2",
            "driver_hourly_stats:avg_daily_trips:3",
        ]

        # Verify results structure
        assert len(data["results"]) == ENTITY_COUNT_2
        for result in data["results"]:
            assert len(result["values"]) == ENTITY_COUNT_4
            assert len(result["statuses"]) == ENTITY_COUNT_4
            assert len(result["event_timestamps"]) == ENTITY_COUNT_4

    def test_feature_consistency(self):
        """Test feature value consistency"""
        payload = {
            "features": ["driver_hourly_stats:conv_rate:1"],
            "entities": {"cust_no": ["X123456"]},
            "event_timestamp": 1751429485000,
        }

        responses = []
        for _ in range(3):
            response = self.client.post("/features", json=payload)
            responses.append(response.json())

        # Verify consistent results
        for i in range(1, len(responses)):
            first_val = responses[0]["results"][0]["values"][1]["value"]
            current_val = responses[i]["results"][0]["values"][1]["value"]
            assert current_val == first_val
