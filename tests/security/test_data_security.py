import pytest
from fastapi.testclient import TestClient

from app.main import app


class TestDataSecurity:
    @pytest.fixture(autouse=True)
    def setup(self):
        with TestClient(app) as client:
            self.client = client
            yield

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
        resp = self.client.post(
            "/create_feature_metadata",
            json={
                "feature_name": "security:rbac:invalid:v1",
                "feature_type": "batch",
                "feature_data_type": "float",
                "query": "SELECT value FROM table",
                "description": "Security test feature",
                "created_by": "test_system",
                "user_role": "tester",
            },
        )
        assert resp.status_code == 400
        assert "cannot perform action" in resp.json()["detail"].lower()
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
            "/submit_test_feature_metadata",
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
                "user_role": "tester",
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
        resp = self.client.post(
            "/update_feature_metadata",
            json={"feature_name": feature_name, "description": "Updated description"},
        )
        assert resp.status_code == 422

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
            "/submit_test_feature_metadata",
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
                "user_role": "tester",
            },
        )
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
        assert metadata["status"] == "DRAFT"
