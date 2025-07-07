import pytest
from fastapi.testclient import TestClient

from app.main import app

# Test constants
HTTP_OK = 200


class TestHealth:
    """Health endpoint test suite"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test client"""
        self.client = TestClient(app)

    def test_health_endpoint(self):
        """Test health check"""
        response = self.client.get("/health")
        assert response.status_code == HTTP_OK
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert data["status"] == "ok"

    def test_available_features_endpoint(self):
        """Test available features listing"""
        response = self.client.get("/features/available")
        assert response.status_code == HTTP_OK
        data = response.json()
        assert "available_features" in data
        assert len(data["available_features"]) > 0
        assert "driver_hourly_stats:conv_rate:1" in data["available_features"]
