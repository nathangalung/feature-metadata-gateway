import pytest
from fastapi.testclient import TestClient

from app.main import app


class TestStatusTransitions:
    """Status transitions tests."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup client."""
        with TestClient(app) as client:
            self.client = client
            yield

    def test_normal_status_progression(self):
        """Normal status flow."""
        feature_name = "status:progression:v1"
        resp = self.client.post(
            "/create_feature_metadata",
            json={
                "feature_name": feature_name,
                "feature_type": "batch",
                "feature_data_type": "float",
                "query": "SELECT value FROM test_table",
                "description": "Status transition test",
                "created_by": "dev_user",
                "user_role": "developer",
            },
        )
        assert resp.status_code in (200, 201), resp.text
        assert resp.json()["metadata"]["status"] == "DRAFT"
        resp = self.client.post(
            "/ready_test_feature_metadata",
            json={
                "feature_name": feature_name,
                "submitted_by": "dev_user",
                "user_role": "developer",
            },
        )
        assert resp.status_code == 200, resp.text
        assert resp.json()["metadata"]["status"] == "READY_FOR_TESTING"
        resp = self.client.post(
            "/test_feature_metadata",
            json={
                "feature_name": feature_name,
                "test_result": "TEST_SUCCEEDED",
                "tested_by": "test_system",
                "user_role": "external_testing_system",
            },
        )
        assert resp.status_code == 200, resp.text
        assert resp.json()["metadata"]["status"] == "TEST_SUCCEEDED"
        resp = self.client.post(
            "/approve_feature_metadata",
            json={
                "feature_name": feature_name,
                "approved_by": "approver_user",
                "user_role": "approver",
            },
        )
        assert resp.status_code == 200, resp.text
        assert resp.json()["metadata"]["status"] == "DEPLOYED"

    def test_critical_field_update_resets_status(self):
        """Critical field resets status."""
        feature_name = "status:reset:v1"
        resp = self.client.post(
            "/create_feature_metadata",
            json={
                "feature_name": feature_name,
                "feature_type": "batch",
                "feature_data_type": "float",
                "query": "SELECT value FROM test_table",
                "description": "Status reset test",
                "created_by": "dev_user",
                "user_role": "developer",
            },
        )
        assert resp.status_code in (200, 201), resp.text
        resp = self.client.post(
            "/ready_test_feature_metadata",
            json={
                "feature_name": feature_name,
                "submitted_by": "dev_user",
                "user_role": "developer",
            },
        )
        assert resp.status_code == 200, resp.text
        resp = self.client.post(
            "/test_feature_metadata",
            json={
                "feature_name": feature_name,
                "test_result": "TEST_SUCCEEDED",
                "tested_by": "test_system",
                "user_role": "external_testing_system",
            },
        )
        assert resp.status_code == 200, resp.text
        assert resp.json()["metadata"]["status"] == "TEST_SUCCEEDED"
        resp = self.client.post(
            "/update_feature_metadata",
            json={
                "feature_name": feature_name,
                "query": "SELECT new_value FROM test_table",
                "last_updated_by": "dev_user",
                "user_role": "developer",
            },
        )
        assert resp.status_code == 200, resp.text
        assert resp.json()["metadata"]["status"] == "READY_FOR_TESTING"
        resp = self.client.post(
            "/ready_test_feature_metadata",
            json={
                "feature_name": feature_name,
                "submitted_by": "dev_user",
                "user_role": "developer",
            },
        )
        assert resp.status_code == 400, resp.text
        assert "DRAFT" in resp.json()["detail"]

    def test_deployed_feature_protection(self):
        """Deployed feature protection."""
        feature_name = "status:deployed:v1"
        resp = self.client.post(
            "/create_feature_metadata",
            json={
                "feature_name": feature_name,
                "feature_type": "batch",
                "feature_data_type": "float",
                "query": "SELECT value FROM test_table",
                "description": "Deployed feature protection test",
                "created_by": "dev_user",
                "user_role": "developer",
            },
        )
        assert resp.status_code in (200, 201), resp.text
        resp = self.client.post(
            "/ready_test_feature_metadata",
            json={
                "feature_name": feature_name,
                "submitted_by": "dev_user",
                "user_role": "developer",
            },
        )
        assert resp.status_code == 200, resp.text
        resp = self.client.post(
            "/test_feature_metadata",
            json={
                "feature_name": feature_name,
                "test_result": "TEST_SUCCEEDED",
                "tested_by": "test_system",
                "user_role": "external_testing_system",
            },
        )
        assert resp.status_code == 200, resp.text
        resp = self.client.post(
            "/approve_feature_metadata",
            json={
                "feature_name": feature_name,
                "approved_by": "approver_user",
                "user_role": "approver",
            },
        )
        assert resp.status_code == 200, resp.text
        resp = self.client.post(
            "/update_feature_metadata",
            json={
                "feature_name": feature_name,
                "description": "Try to update deployed feature",
                "last_updated_by": "dev_user",
                "user_role": "developer",
            },
        )
        assert resp.status_code == 400, resp.text
        assert "DEPLOYED" in resp.json()["detail"]
        resp = self.client.post(
            "/delete_feature_metadata",
            json={
                "feature_name": feature_name,
                "deleted_by": "dev_user",
                "user_role": "developer",
                "deletion_reason": "Trying to delete deployed feature",
            },
        )
        assert resp.status_code == 400, resp.text
        assert "DEPLOYED" in resp.json()["detail"]
