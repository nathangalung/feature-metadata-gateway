"""Test feature status transitions."""

import pytest
from fastapi.testclient import TestClient

from app.main import app

class TestStatusTransitions:
    """Test feature status transitions."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test client with lifespan."""
        with TestClient(app) as client:
            self.client = client
            yield

    def test_normal_status_progression(self):
        """Test normal status progression."""
        feature_name = "status:progression:v1"
        # Create feature
        resp = self.client.post("/create_feature_metadata", json={
            "feature_name": feature_name,
            "feature_type": "batch",
            "feature_data_type": "float",
            "query": "SELECT value FROM test_table",
            "description": "Status transition test",
            "created_by": "dev_user",
            "user_role": "developer"
        })
        assert resp.status_code in (200, 201), resp.text
        assert resp.json()["metadata"]["status"] == "DRAFT"
        # Ready for testing
        resp = self.client.post("/ready_test_feature_metadata", json={
            "feature_name": feature_name,
            "submitted_by": "dev_user",
            "user_role": "developer"
        })
        assert resp.status_code == 200, resp.text
        assert resp.json()["metadata"]["status"] == "READY_FOR_TESTING"
        # Pass testing
        resp = self.client.post("/test_feature_metadata", json={
            "feature_name": feature_name,
            "test_result": "TEST_SUCCEEDED",
            "tested_by": "test_system",
            "user_role": "external_testing_system"
        })
        assert resp.status_code == 200, resp.text
        assert resp.json()["metadata"]["status"] == "TEST_SUCCEEDED"
        # Approve feature
        resp = self.client.post("/approve_feature_metadata", json={
            "feature_name": feature_name,
            "approved_by": "approver_user",
            "user_role": "approver"
        })
        assert resp.status_code == 200, resp.text
        assert resp.json()["metadata"]["status"] == "DEPLOYED"

    def test_critical_field_update_resets_status(self):
        """Test updating critical fields resets status."""
        feature_name = "status:reset:v1"
        # Create feature
        resp = self.client.post("/create_feature_metadata", json={
            "feature_name": feature_name,
            "feature_type": "batch",
            "feature_data_type": "float",
            "query": "SELECT value FROM test_table",
            "description": "Status reset test",
            "created_by": "dev_user",
            "user_role": "developer"
        })
        assert resp.status_code in (200, 201), resp.text
        # Ready for testing
        resp = self.client.post("/ready_test_feature_metadata", json={
            "feature_name": feature_name,
            "submitted_by": "dev_user",
            "user_role": "developer"
        })
        assert resp.status_code == 200, resp.text
        # Pass testing
        resp = self.client.post("/test_feature_metadata", json={
            "feature_name": feature_name,
            "test_result": "TEST_SUCCEEDED",
            "tested_by": "test_system",
            "user_role": "external_testing_system"
        })
        assert resp.status_code == 200, resp.text
        assert resp.json()["metadata"]["status"] == "TEST_SUCCEEDED"
        # Update critical field (query)
        resp = self.client.post("/update_feature_metadata", json={
            "feature_name": feature_name,
            "query": "SELECT new_value FROM test_table",
            "last_updated_by": "dev_user",
            "user_role": "developer"
        })
        assert resp.status_code == 200, resp.text
        assert resp.json()["metadata"]["status"] == "READY_FOR_TESTING"
        # Update non-critical field (description)
        resp = self.client.post("/ready_test_feature_metadata", json={
            "feature_name": feature_name,
            "submitted_by": "dev_user",
            "user_role": "developer"
        })
        # After critical field update, status is READY_FOR_TESTING, so ready_test should fail (must be DRAFT)
        assert resp.status_code == 400, resp.text
        assert "DRAFT" in resp.json()["detail"]

    def test_deployed_feature_protection(self):
        """Test deployed feature protection."""
        feature_name = "status:deployed:v1"
        # Create and deploy feature
        resp = self.client.post("/create_feature_metadata", json={
            "feature_name": feature_name,
            "feature_type": "batch",
            "feature_data_type": "float",
            "query": "SELECT value FROM test_table",
            "description": "Deployed feature protection test",
            "created_by": "dev_user",
            "user_role": "developer"
        })
        assert resp.status_code in (200, 201), resp.text
        resp = self.client.post("/ready_test_feature_metadata", json={
            "feature_name": feature_name,
            "submitted_by": "dev_user",
            "user_role": "developer"
        })
        assert resp.status_code == 200, resp.text
        resp = self.client.post("/test_feature_metadata", json={
            "feature_name": feature_name,
            "test_result": "TEST_SUCCEEDED",
            "tested_by": "test_system",
            "user_role": "external_testing_system"
        })
        assert resp.status_code == 200, resp.text
        resp = self.client.post("/approve_feature_metadata", json={
            "feature_name": feature_name,
            "approved_by": "approver_user",
            "user_role": "approver"
        })
        assert resp.status_code == 200, resp.text
        # Update deployed feature (fail)
        resp = self.client.post("/update_feature_metadata", json={
            "feature_name": feature_name,
            "description": "Try to update deployed feature",
            "last_updated_by": "dev_user",
            "user_role": "developer"
        })
        assert resp.status_code == 400, resp.text
        assert "DEPLOYED" in resp.json()["detail"]
        # Delete deployed feature (fail) - must include deletion_reason to avoid 422
        resp = self.client.post("/delete_feature_metadata", json={
            "feature_name": feature_name,
            "deleted_by": "dev_user",
            "user_role": "developer",
            "deletion_reason": "Trying to delete deployed feature"
        })
        assert resp.status_code == 400, resp.text
        assert "DEPLOYED" in resp.json()["detail"]