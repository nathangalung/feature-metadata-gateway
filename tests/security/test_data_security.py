import pytest
from fastapi.testclient import TestClient

from app.main import app


class TestDataSecurity:
    """Test data security aspects."""

    # Setup test client
    @pytest.fixture(autouse=True)
    def setup(self):
        with TestClient(app) as client:
            self.client = client
            yield

    # Test RBAC for features
    def test_role_based_access_control(self):
        feature_name = "security:rbac:v1"
        self.client.post(
            "/create_feature_metadata",
            json={
                "feature_name": feature_name,
                "feature_type": "batch",
                "feature_data_type": "float",
                "query": "SELECT value FROM table",
                "description": "Security test feature",
                "created_by": "developer",
                "user_role": "developer",
            },
        )
        # External testing system cannot create
        resp = self.client.post(
            "/create_feature_metadata",
            json={
                "feature_name": "security:rbac:invalid:v1",
                "feature_type": "batch",
                "feature_data_type": "float",
                "query": "SELECT value FROM table",
                "description": "Security test feature",
                "created_by": "test_system",
                "user_role": "external_testing_system",
            },
        )
        assert resp.status_code == 400
        assert "cannot perform action" in resp.json()["detail"].lower()
        # Developer cannot approve
        resp = self.client.post(
            "/approve_feature_metadata",
            json={
                "feature_name": feature_name,
                "approved_by": "developer",
                "user_role": "developer",
            },
        )
        assert resp.status_code == 400
        assert "cannot perform action" in resp.json()["detail"].lower()
        # Approver cannot test
        resp = self.client.post(
            "/test_feature_metadata",
            json={
                "feature_name": feature_name,
                "test_result": "TEST_SUCCEEDED",
                "tested_by": "approver",
                "user_role": "approver",
            },
        )
        assert resp.status_code == 400
        assert "cannot perform action" in resp.json()["detail"].lower()

    # Test deployed feature protection
    def test_deployed_feature_protection(self):
        feature_name = "security:deployed:v1"
        self.client.post(
            "/create_feature_metadata",
            json={
                "feature_name": feature_name,
                "feature_type": "batch",
                "feature_data_type": "float",
                "query": "SELECT value FROM table",
                "description": "Security test feature",
                "created_by": "developer",
                "user_role": "developer",
            },
        )
        self.client.post(
            "/ready_test_feature_metadata",
            json={
                "feature_name": feature_name,
                "submitted_by": "developer",
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
        self.client.post(
            "/approve_feature_metadata",
            json={
                "feature_name": feature_name,
                "approved_by": "approver",
                "user_role": "approver",
            },
        )
        # Update deployed feature
        resp = self.client.post(
            "/update_feature_metadata",
            json={
                "feature_name": feature_name,
                "description": "Updated description",
                "last_updated_by": "developer",
                "user_role": "developer",
            },
        )
        assert resp.status_code == 400
        assert "deployed" in resp.json()["detail"].lower()
        # Delete deployed feature
        resp = self.client.post(
            "/delete_feature_metadata",
            json={
                "feature_name": feature_name,
                "deleted_by": "developer",
                "user_role": "developer",
                "deletion_reason": "Trying to delete deployed feature",
            },
        )
        assert resp.status_code == 400
        assert "deployed" in resp.json()["detail"].lower()

    # Test metadata field security
    def test_metadata_field_security(self):
        feature_name = "security:fields:v1"
        resp = self.client.post(
            "/create_feature_metadata",
            json={
                "feature_name": feature_name,
                "feature_type": "batch",
                "feature_data_type": "float",
                "query": "SELECT value FROM table",
                "description": "Security test feature",
                "created_by": "developer",
                "user_role": "developer",
            },
        )
        metadata = resp.json()["metadata"]
        assert "created_time" in metadata
        assert "updated_time" in metadata
        assert "status" in metadata
        assert metadata["created_by"] == "developer"
        # Update missing required fields
        resp = self.client.post(
            "/update_feature_metadata",
            json={"feature_name": feature_name, "description": "Updated description"},
        )
        assert resp.status_code == 422

    # Test critical field update protection
    def test_critical_field_update_protection(self):
        feature_name = "security:critical:v1"
        self.client.post(
            "/create_feature_metadata",
            json={
                "feature_name": feature_name,
                "feature_type": "batch",
                "feature_data_type": "float",
                "query": "SELECT value FROM table",
                "description": "Security test feature",
                "created_by": "developer",
                "user_role": "developer",
            },
        )
        self.client.post(
            "/ready_test_feature_metadata",
            json={
                "feature_name": feature_name,
                "submitted_by": "developer",
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
        # Update critical field (query)
        resp = self.client.post(
            "/update_feature_metadata",
            json={
                "feature_name": feature_name,
                "query": "SELECT new_value FROM table",
                "last_updated_by": "developer",
                "user_role": "developer",
            },
        )
        assert resp.status_code == 200
        metadata = resp.json()["metadata"]
        assert metadata["status"] == "READY_FOR_TESTING"
