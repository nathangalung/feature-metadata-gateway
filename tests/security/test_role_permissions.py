import pytest
from fastapi.testclient import TestClient

from app.main import app


class TestRolePermissions:
    """Test role-based permissions."""

    # Setup client
    @pytest.fixture(autouse=True)
    def setup(self):
        with TestClient(app) as client:
            self.client = client
            yield

    # Developer permissions
    def test_developer_permissions(self):
        response = self.client.post(
            "/create_feature_metadata",
            json={
                "feature_name": "permissions:dev:v1",
                "feature_type": "batch",
                "feature_data_type": "float",
                "query": "SELECT value FROM table",
                "description": "Developer permissions test",
                "created_by": "developer",
                "user_role": "developer",
            },
        )
        assert response.status_code == 201
        response = self.client.post(
            "/update_feature_metadata",
            json={
                "feature_name": "permissions:dev:v1",
                "description": "Updated description",
                "last_updated_by": "developer",
                "user_role": "developer",
            },
        )
        assert response.status_code == 200
        response = self.client.post(
            "/submit_test_feature_metadata",
            json={
                "feature_name": "permissions:dev:v1",
                "submitted_by": "developer",
                "user_role": "developer",
            },
        )
        assert response.status_code == 200
        response = self.client.post(
            "/test_feature_metadata",
            json={
                "feature_name": "permissions:dev:v1",
                "test_result": "TEST_SUCCEEDED",
                "tested_by": "developer",
                "user_role": "developer",
            },
        )
        assert response.status_code == 400
        response = self.client.post(
            "/approve_feature_metadata",
            json={
                "feature_name": "permissions:dev:v1",
                "approved_by": "developer",
                "user_role": "developer",
            },
        )
        assert response.status_code == 400

    # Testing system permissions
    def test_testing_system_permissions(self):
        self.client.post(
            "/create_feature_metadata",
            json={
                "feature_name": "permissions:test:v1",
                "feature_type": "batch",
                "feature_data_type": "float",
                "query": "SELECT value FROM table",
                "description": "Testing system permissions test",
                "created_by": "developer",
                "user_role": "developer",
            },
        )
        self.client.post(
            "/submit_test_feature_metadata",
            json={
                "feature_name": "permissions:test:v1",
                "submitted_by": "developer",
                "user_role": "developer",
            },
        )
        response = self.client.post(
            "/create_feature_metadata",
            json={
                "feature_name": "permissions:test:invalid:v1",
                "feature_type": "batch",
                "feature_data_type": "float",
                "query": "SELECT value FROM table",
                "description": "Invalid permissions test",
                "created_by": "test_system",
                "user_role": "tester",
            },
        )
        assert response.status_code == 400
        response = self.client.post(
            "/test_feature_metadata",
            json={
                "feature_name": "permissions:test:v1",
                "test_result": "TEST_SUCCEEDED",
                "tested_by": "test_system",
                "user_role": "tester",
            },
        )
        assert response.status_code == 200
        response = self.client.post(
            "/approve_feature_metadata",
            json={
                "feature_name": "permissions:test:v1",
                "approved_by": "test_system",
                "user_role": "tester",
            },
        )
        assert response.status_code == 400

    # Approver permissions
    def test_approver_permissions(self):
        self.client.post(
            "/create_feature_metadata",
            json={
                "feature_name": "permissions:approve:v1",
                "feature_type": "batch",
                "feature_data_type": "float",
                "query": "SELECT value FROM table",
                "description": "Approver permissions test",
                "created_by": "developer",
                "user_role": "developer",
            },
        )
        self.client.post(
            "/submit_test_feature_metadata",
            json={
                "feature_name": "permissions:approve:v1",
                "submitted_by": "developer",
                "user_role": "developer",
            },
        )
        self.client.post(
            "/test_feature_metadata",
            json={
                "feature_name": "permissions:approve:v1",
                "test_result": "TEST_SUCCEEDED",
                "tested_by": "test_system",
                "user_role": "tester",
            },
        )
        response = self.client.post(
            "/create_feature_metadata",
            json={
                "feature_name": "permissions:approve:invalid:v1",
                "feature_type": "batch",
                "feature_data_type": "float",
                "query": "SELECT value FROM table",
                "description": "Invalid permissions test",
                "created_by": "approver",
                "user_role": "approver",
            },
        )
        assert response.status_code == 400
        response = self.client.post(
            "/approve_feature_metadata",
            json={
                "feature_name": "permissions:approve:v1",
                "approved_by": "approver",
                "user_role": "approver",
            },
        )
        assert response.status_code == 200
        self.client.post(
            "/create_feature_metadata",
            json={
                "feature_name": "permissions:reject:v1",
                "feature_type": "batch",
                "feature_data_type": "float",
                "query": "SELECT value FROM table",
                "description": "Rejection permissions test",
                "created_by": "developer",
                "user_role": "developer",
            },
        )
        self.client.post(
            "/submit_test_feature_metadata",
            json={
                "feature_name": "permissions:reject:v1",
                "submitted_by": "developer",
                "user_role": "developer",
            },
        )
        self.client.post(
            "/test_feature_metadata",
            json={
                "feature_name": "permissions:reject:v1",
                "test_result": "TEST_SUCCEEDED",
                "tested_by": "test_system",
                "user_role": "tester",
            },
        )
        response = self.client.post(
            "/reject_feature_metadata",
            json={
                "feature_name": "permissions:reject:v1",
                "rejected_by": "approver",
                "user_role": "approver",
                "rejection_reason": "Rejected for testing purposes",
            },
        )
        assert response.status_code == 200
