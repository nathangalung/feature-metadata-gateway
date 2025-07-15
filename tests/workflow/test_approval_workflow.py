import pytest
from fastapi.testclient import TestClient

from app.main import app


class TestApprovalWorkflow:
    """Approval workflow tests."""

    @pytest.fixture(autouse=True)
    def setup(self):
        with TestClient(app) as client:
            self.client = client
            yield

    # Approve and deploy feature
    def test_successful_approval_workflow(self):
        feature_name = "approval:workflow:v1"
        self.client.post(
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
                "approval_notes": "Feature approved for deployment",
            },
        )
        assert resp.status_code == 200
        metadata = resp.json()["metadata"]
        assert metadata["status"] == "DEPLOYED"
        assert metadata["approved_by"] == "approver_user"
        assert metadata["deployed_by"] == "approver_user"

    # Reject feature
    def test_rejection_workflow(self):
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

    # Approve permission restrictions
    def test_approval_permission_restrictions(self):
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
                "user_role": "tester",
            },
        )
        assert resp.status_code == 400
