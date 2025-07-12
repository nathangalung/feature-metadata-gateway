import pytest
from fastapi.testclient import TestClient

from app.main import app


class TestCrossServiceIntegration:
    """Test cross-service interactions."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test client."""
        self.client = TestClient(app)

    def test_feature_metadata_to_feature_service(self):
        """Test metadata to feature service."""
        # Create feature
        resp = self.client.post(
            "/create_feature_metadata",
            json={
                "feature_name": "cross:service:v1",
                "feature_type": "batch",
                "feature_data_type": "float",
                "query": "SELECT value FROM table",
                "description": "Cross service test feature",
                "created_by": "test_user",
                "user_role": "developer",
            },
        )
        assert resp.status_code == 201

        # Check feature available
        resp = self.client.get("/features/available")
        assert resp.status_code == 200
        data = resp.json()
        assert "cross:service:v1" in data["available_features"]

        # Request feature value
        resp = self.client.post(
            "/features",
            json={
                "features": ["cross:service:v1"],
                "entities": {"entity_id": ["test_entity"]},
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        feature_value = data["results"][0]["values"][1]
        assert feature_value["feature_type"] == "batch"
        assert feature_value["feature_data_type"] == "float"

    def test_deployed_status_sync(self):
        """Test deployed status sync."""
        # Create feature
        self.client.post(
            "/create_feature_metadata",
            json={
                "feature_name": "cross:deployed:v1",
                "feature_type": "real-time",
                "feature_data_type": "int",
                "query": "SELECT count FROM table",
                "description": "Cross service deployed test",
                "created_by": "test_user",
                "user_role": "developer",
            },
        )
        # Ready for testing
        self.client.post(
            "/ready_test_feature_metadata",
            json={
                "feature_name": "cross:deployed:v1",
                "submitted_by": "test_user",
                "user_role": "developer",
            },
        )
        # Test success
        self.client.post(
            "/test_feature_metadata",
            json={
                "feature_name": "cross:deployed:v1",
                "test_result": "TEST_SUCCEEDED",
                "tested_by": "test_system",
                "user_role": "external_testing_system",
            },
        )
        # Approve and deploy
        self.client.post(
            "/approve_feature_metadata",
            json={
                "feature_name": "cross:deployed:v1",
                "approved_by": "approver_user",
                "user_role": "approver",
            },
        )
        # Check deployed features
        resp = self.client.get("/get_deployed_features")
        assert resp.status_code == 200
        data = resp.json()
        assert "cross:deployed:v1" in data["features"]
        # Check available in feature service
        resp = self.client.get("/features/available")
        assert resp.status_code == 200
        data = resp.json()
        assert "cross:deployed:v1" in data["available_features"]

    def test_error_handling_across_services(self):
        """Test error handling propagation."""
        # Request non-existent feature
        resp = self.client.post(
            "/features",
            json={
                "features": ["nonexistent:feature:v1"],
                "entities": {"entity_id": ["test_entity"]},
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        feature_status = data["results"][0]["statuses"][1]
        assert feature_status == "404 Not Found"
        feature_value = data["results"][0]["values"][1]
        assert feature_value["value"] is None
        assert feature_value["status"] == "NOT_FOUND"
