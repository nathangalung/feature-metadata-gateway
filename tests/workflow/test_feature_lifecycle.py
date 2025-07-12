"""Test complete feature lifecycle."""

import pytest
from fastapi.testclient import TestClient

from app.main import app

class TestFeatureLifecycle:
    """Test complete feature lifecycle."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test client."""
        self.client = TestClient(app)

    def test_complete_feature_lifecycle(self):
        """Test complete feature lifecycle."""
        feature_name = "lifecycle:complete:v1"
        # Create feature
        resp = self.client.post("/create_feature_metadata", json={
            "feature_name": feature_name,
            "feature_type": "batch",
            "feature_data_type": "float",
            "query": "SELECT value FROM test_table",
            "description": "Lifecycle test feature",
            "created_by": "dev_user",
            "user_role": "developer"
        })
        assert resp.status_code == 201
        assert resp.json()["metadata"]["status"] == "DRAFT"
        # Update feature
        resp = self.client.post("/update_feature_metadata", json={
            "feature_name": feature_name,
            "description": "Updated description",
            "last_updated_by": "dev_user",
            "user_role": "developer"
        })
        assert resp.status_code == 200
        assert resp.json()["metadata"]["description"] == "Updated description"
        # Ready for testing
        resp = self.client.post("/ready_test_feature_metadata", json={
            "feature_name": feature_name,
            "submitted_by": "dev_user",
            "user_role": "developer"
        })
        assert resp.status_code == 200
        assert resp.json()["metadata"]["status"] == "READY_FOR_TESTING"
        # Pass testing
        resp = self.client.post("/test_feature_metadata", json={
            "feature_name": feature_name,
            "test_result": "TEST_SUCCEEDED",
            "tested_by": "test_system",
            "user_role": "external_testing_system",
            "test_notes": "All tests passed"
        })
        assert resp.status_code == 200
        assert resp.json()["metadata"]["status"] == "TEST_SUCCEEDED"
        # Approve and deploy
        resp = self.client.post("/approve_feature_metadata", json={
            "feature_name": feature_name,
            "approved_by": "approver_user",
            "user_role": "approver",
            "approval_notes": "Approved for production"
        })
        assert resp.status_code == 200
        assert resp.json()["metadata"]["status"] == "DEPLOYED"
        # Check deployed list
        resp = self.client.get("/get_deployed_features")
        assert resp.status_code == 200
        assert feature_name in resp.json()["features"]
        # Update deployed feature (fail)
        resp = self.client.post("/update_feature_metadata", json={
            "feature_name": feature_name,
            "description": "Try to update deployed feature",
            "last_updated_by": "dev_user",
            "user_role": "developer"
        })
        assert resp.status_code == 400
        # Delete deployed feature (fail) - must include deletion_reason to avoid 422
        resp = self.client.post("/delete_feature_metadata", json={
            "feature_name": feature_name,
            "deleted_by": "dev_user",
            "user_role": "developer",
            "deletion_reason": "Trying to delete deployed feature"
        })
        assert resp.status_code == 400

    def test_feature_failure_and_fix_lifecycle(self):
        """Test feature failure and fix lifecycle."""
        feature_name = "lifecycle:fix:v1"
        # Create feature
        self.client.post("/create_feature_metadata", json={
            "feature_name": feature_name,
            "feature_type": "batch",
            "feature_data_type": "float",
            "query": "SELECT value FROM test_table",
            "description": "Feature that will fail tests",
            "created_by": "dev_user",
            "user_role": "developer"
        })
        # Ready for testing
        self.client.post("/ready_test_feature_metadata", json={
            "feature_name": feature_name,
            "submitted_by": "dev_user",
            "user_role": "developer"
        })
        # Fail testing
        resp = self.client.post("/test_feature_metadata", json={
            "feature_name": feature_name,
            "test_result": "TEST_FAILED",
            "tested_by": "test_system",
            "user_role": "external_testing_system",
            "test_notes": "Tests failed - query returns inconsistent results"
        })
        assert resp.status_code == 200
        assert resp.json()["metadata"]["status"] == "TEST_FAILED"
        # Fix feature
        resp = self.client.post("/fix_feature_metadata", json={
            "feature_name": feature_name,
            "fixed_by": "dev_user",
            "user_role": "developer",
            "fix_description": "Fixed query performance"
        })
        assert resp.status_code == 200
        