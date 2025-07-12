"""Security tests for role permissions."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


class TestRolePermissions:
    """Test role-based permissions."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test client."""
        with TestClient(app) as client:
            self.client = client
            yield

    def test_developer_permissions(self):
        """Test developer role permissions."""
        # Create a feature with developer role
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

        # Update a feature with developer role
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

        # Submit for testing with developer role
        response = self.client.post(
            "/ready_test_feature_metadata",
            json={
                "feature_name": "permissions:dev:v1",
                "submitted_by": "developer",
                "user_role": "developer",
            },
        )
        assert response.status_code == 200

        # Developer cannot test feature
        response = self.client.post(
            "/test_feature_metadata",
            json={
                "feature_name": "permissions:dev:v1",
                "test_result": "TEST_SUCCEEDED",
                "tested_by": "developer",
                "user_role": "developer",  # Wrong role
            },
        )
        assert response.status_code == 400

        # Developer cannot approve feature
        response = self.client.post(
            "/approve_feature_metadata",
            json={
                "feature_name": "permissions:dev:v1",
                "approved_by": "developer",
                "user_role": "developer",  # Wrong role
            },
        )
        assert response.status_code == 400

    def test_testing_system_permissions(self):
        """Test external testing system role permissions."""
        # Create a feature for testing
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

        # Submit for testing
        self.client.post(
            "/ready_test_feature_metadata",
            json={
                "feature_name": "permissions:test:v1",
                "submitted_by": "developer",
                "user_role": "developer",
            },
        )

        # Testing system cannot create features
        response = self.client.post(
            "/create_feature_metadata",
            json={
                "feature_name": "permissions:test:invalid:v1",
                "feature_type": "batch",
                "feature_data_type": "float",
                "query": "SELECT value FROM table",
                "description": "Invalid permissions test",
                "created_by": "test_system",
                "user_role": "external_testing_system",  # Wrong role
            },
        )
        assert response.status_code == 400

        # Testing system can test features
        response = self.client.post(
            "/test_feature_metadata",
            json={
                "feature_name": "permissions:test:v1",
                "test_result": "TEST_SUCCEEDED",
                "tested_by": "test_system",
                "user_role": "external_testing_system",
            },
        )
        assert response.status_code == 200

        # Testing system cannot approve features
        response = self.client.post(
            "/approve_feature_metadata",
            json={
                "feature_name": "permissions:test:v1",
                "approved_by": "test_system",
                "user_role": "external_testing_system",  # Wrong role
            },
        )
        assert response.status_code == 400

    def test_approver_permissions(self):
        """Test approver role permissions."""
        # Create a feature for approval
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

        # Submit for testing
        self.client.post(
            "/ready_test_feature_metadata",
            json={
                "feature_name": "permissions:approve:v1",
                "submitted_by": "developer",
                "user_role": "developer",
            },
        )

        # Test successful
        self.client.post(
            "/test_feature_metadata",
            json={
                "feature_name": "permissions:approve:v1",
                "test_result": "TEST_SUCCEEDED",
                "tested_by": "test_system",
                "user_role": "external_testing_system",
            },
        )

        # Approver cannot create features
        response = self.client.post(
            "/create_feature_metadata",
            json={
                "feature_name": "permissions:approve:invalid:v1",
                "feature_type": "batch",
                "feature_data_type": "float",
                "query": "SELECT value FROM table",
                "description": "Invalid permissions test",
                "created_by": "approver",
                "user_role": "approver",  # Wrong role
            },
        )
        assert response.status_code == 400

        # Approver can approve features
        response = self.client.post(
            "/approve_feature_metadata",
            json={
                "feature_name": "permissions:approve:v1",
                "approved_by": "approver",
                "user_role": "approver",
            },
        )
        assert response.status_code == 200

        # Approver can reject features
        # Create another feature for rejection
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

        # Submit for testing
        self.client.post(
            "/ready_test_feature_metadata",
            json={
                "feature_name": "permissions:reject:v1",
                "submitted_by": "developer",
                "user_role": "developer",
            },
        )

        # Test successful
        self.client.post(
            "/test_feature_metadata",
            json={
                "feature_name": "permissions:reject:v1",
                "test_result": "TEST_SUCCEEDED",
                "tested_by": "test_system",
                "user_role": "external_testing_system",
            },
        )

        # Reject
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
