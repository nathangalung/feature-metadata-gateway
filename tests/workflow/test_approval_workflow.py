import pytest
from fastapi.testclient import TestClient

from app.main import app


class TestApprovalWorkflow:
    """Approval workflow tests."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup client."""
        with TestClient(app) as client:
            self.client = client
            yield

    def test_successful_approval_workflow(self):
        """Approve and deploy feature."""
        feature_name = "approval:workflow:v1"
        resp = self.client.post(
            "/create_feature_metadata",
            json={
                "feature_name": feature_name,
                "feature_type": "batch",
                "feature_data_type": "float",
                "query": "SELECT value FROM test_table",
                "description": "Approval workflow test",
                "created_by": "dev_user",
                "user_role": "developer",
            },
        )
        assert resp.status_code == 201
        resp = self.client.post(
            "/ready_test_feature_metadata",
            json={
                "feature_name": feature_name,
                "submitted_by": "dev_user",
                "user_role": "developer",
            },
        )
        assert resp.status_code == 200
        assert resp.json()["metadata"]["status"] == "READY_FOR_TESTING"
        resp = self.client.post(
            "/test_feature_metadata",
            json={
                "feature_name": feature_name,
                "test_result": "TEST_SUCCEEDED",
                "tested_by": "test_system",
                "user_role": "external_testing_system",
                "test_notes": "All tests passed",
            },
        )
        assert resp.status_code == 200
        assert resp.json()["metadata"]["status"] == "TEST_SUCCEEDED"
        resp = self.client.post(
            "/approve_feature_metadata",
            json={
                "feature_name": feature_name,
                "approved_by": "approver_user",
                "user_role": "approver",
                "approval_notes": "Feature approved for deployment",
            },
        )
        assert resp.status_code == 200
        metadata = resp.json()["metadata"]
        assert metadata["status"] == "DEPLOYED"
        assert metadata["approved_by"] == "approver_user"
        assert metadata["deployed_by"] == "approver_user"
        resp = self.client.get("/get_deployed_features")
        assert resp.status_code == 200
        assert feature_name in resp.json()["features"]

    def test_rejection_workflow(self):
        """Reject feature."""
        feature_name = "approval:reject:v1"
        self.client.post(
            "/create_feature_metadata",
            json={
                "feature_name": feature_name,
                "feature_type": "batch",
                "feature_data_type": "float",
                "query": "SELECT value FROM test_table",
                "description": "Rejection workflow test",
                "created_by": "dev_user",
                "user_role": "developer",
            },
        )
        self.client.post(
            "/ready_test_feature_metadata",
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
                "user_role": "external_testing_system",
            },
        )
        resp = self.client.post(
            "/reject_feature_metadata",
            json={
                "feature_name": feature_name,
                "rejected_by": "approver_user",
                "user_role": "approver",
                "rejection_reason": "Feature does not meet requirements",
            },
        )
        assert resp.status_code == 200
        metadata = resp.json()["metadata"]
        assert metadata["status"] == "REJECTED"
        assert metadata["rejected_by"] == "approver_user"
        resp = self.client.get("/get_deployed_features")
        assert resp.status_code == 200
        assert feature_name not in resp.json()["features"]

    def test_approval_permission_restrictions(self):
        """Approve permission restrictions."""
        feature_name = "approval:permissions:v1"
        self.client.post(
            "/create_feature_metadata",
            json={
                "feature_name": feature_name,
                "feature_type": "batch",
                "feature_data_type": "float",
                "query": "SELECT value FROM test_table",
                "description": "Permission test",
                "created_by": "dev_user",
                "user_role": "developer",
            },
        )
        self.client.post(
            "/ready_test_feature_metadata",
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
                "user_role": "external_testing_system",
            },
        )
        resp = self.client.post(
            "/approve_feature_metadata",
            json={
                "feature_name": feature_name,
                "approved_by": "dev_user",
                "user_role": "developer",
            },
        )
        assert resp.status_code == 400
        resp = self.client.post(
            "/approve_feature_metadata",
            json={
                "feature_name": feature_name,
                "approved_by": "test_system",
                "user_role": "external_testing_system",
            },
        )
        assert resp.status_code == 400
