import pytest
from fastapi.testclient import TestClient

from app.main import app


class TestFeatureLifecycle:
    """Feature lifecycle tests."""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = TestClient(app)

    # Full lifecycle test
    def test_complete_feature_lifecycle(self):
        feature_name = "lifecycle:complete:v1"
        self.client.post(
            "/create_feature_metadata",
            json={
                "feature_name": feature_name,
                "feature_type": "batch",
                "feature_data_type": "float",
                "query": "SELECT value FROM test_table",
                "description": "Lifecycle test feature",
                "created_by": "dev_user",
                "user_role": "developer",
            },
        )
        self.client.post(
            "/update_feature_metadata",
            json={
                "feature_name": feature_name,
                "description": "Updated description",
                "last_updated_by": "dev_user",
                "user_role": "developer",
            },
        )
        self.client.post(
            "/submit_test_feature_metadata",
            json={
                "feature_name": feature_name,
                "submitted_by": "dev_user",
                "user_role": "developer",
            },
        )
        self.client.post(
            "/test_feature_metadata",
            json={
                "feature_name": feature_name,
                "test_result": "TEST_SUCCEEDED",
                "tested_by": "test_system",
                "user_role": "tester",
                "test_notes": "All tests passed",
            },
        )
        resp = self.client.post(
            "/approve_feature_metadata",
            json={
                "feature_name": feature_name,
                "approved_by": "approver_user",
                "user_role": "approver",
                "approval_notes": "Approved for production",
            },
        )
        assert resp.status_code == 200
        assert resp.json()["metadata"]["status"] == "DEPLOYED"
        resp = self.client.post(
            "/update_feature_metadata",
            json={
                "feature_name": feature_name,
                "description": "Try to update deployed feature",
                "last_updated_by": "dev_user",
                "user_role": "developer",
            },
        )
        assert resp.status_code == 400
        resp = self.client.post(
            "/delete_feature_metadata",
            json={
                "feature_name": feature_name,
                "deleted_by": "dev_user",
                "user_role": "developer",
                "deletion_reason": "Trying to delete deployed feature",
            },
        )
        assert resp.status_code == 400

    # Fail and fix lifecycle
    def test_feature_failure_and_fix_lifecycle(self):
        feature_name = "lifecycle:fix:v1"
        self.client.post(
            "/create_feature_metadata",
            json={
                "feature_name": feature_name,
                "feature_type": "batch",
                "feature_data_type": "float",
                "query": "SELECT value FROM test_table",
                "description": "Feature that will fail tests",
                "created_by": "dev_user",
                "user_role": "developer",
            },
        )
        self.client.post(
            "/submit_test_feature_metadata",
            json={
                "feature_name": feature_name,
                "submitted_by": "dev_user",
                "user_role": "developer",
            },
        )
        resp = self.client.post(
            "/test_feature_metadata",
            json={
                "feature_name": feature_name,
                "test_result": "TEST_FAILED",
                "tested_by": "test_system",
                "user_role": "tester",
                "test_notes": "Tests failed - query returns inconsistent results",
            },
        )
        assert resp.status_code == 200
        assert resp.json()["metadata"]["status"] == "TEST_FAILED"
