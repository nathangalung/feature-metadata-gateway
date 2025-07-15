import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def test_client():
    with TestClient(app) as client:
        yield client


class TestFeatureCreationEndpoints:
    def test_create_feature_success(self, test_client):
        resp = test_client.post(
            "/create_feature_metadata",
            json={
                "feature_name": "integration:create:v1",
                "feature_type": "batch",
                "feature_data_type": "float",
                "query": "SELECT value FROM table",
                "description": "Integration test feature",
                "created_by": "integration_user",
                "user_role": "developer",
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["metadata"]["feature_name"] == "integration:create:v1"
        assert data["metadata"]["status"] == "DRAFT"

    def test_create_duplicate_feature_error(self, test_client):
        feature_data = {
            "feature_name": "integration:duplicate:v1",
            "feature_type": "batch",
            "feature_data_type": "int",
            "query": "SELECT count FROM table",
            "description": "Duplicate test",
            "created_by": "integration_user",
            "user_role": "developer",
        }
        resp1 = test_client.post("/create_feature_metadata", json=feature_data)
        assert resp1.status_code == 201
        resp2 = test_client.post("/create_feature_metadata", json=feature_data)
        assert resp2.status_code == 400
        assert "already exists" in resp2.json()["detail"]

    def test_create_feature_invalid_data(self, test_client):
        resp = test_client.post(
            "/create_feature_metadata",
            json={
                "feature_name": "invalid_name_format",
                "feature_type": "invalid_type",
                "feature_data_type": "invalid_data_type",
                "query": "SELECT 1",
                "description": "Invalid test",
                "created_by": "user",
                "user_role": "invalid_role",
            },
        )
        assert resp.status_code == 400


class TestFeatureUpdateEndpoints:
    def test_update_feature_description(self, test_client):
        test_client.post(
            "/create_feature_metadata",
            json={
                "feature_name": "integration:update:v1",
                "feature_type": "real-time",
                "feature_data_type": "string",
                "query": "SELECT name FROM users",
                "description": "Original description",
                "created_by": "integration_user",
                "user_role": "developer",
            },
        )
        resp = test_client.post(
            "/update_feature_metadata",
            json={
                "feature_name": "integration:update:v1",
                "description": "Updated description",
                "last_updated_by": "integration_user",
                "user_role": "developer",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["metadata"]["description"] == "Updated description"
        assert data["metadata"]["last_updated_by"] == "integration_user"
        assert data["metadata"]["status"] == "DRAFT"

    def test_update_nonexistent_feature(self, test_client):
        resp = test_client.post(
            "/update_feature_metadata",
            json={
                "feature_name": "integration:nonexistent:v1",
                "description": "New description",
                "last_updated_by": "user",
                "user_role": "developer",
            },
        )
        assert resp.status_code == 400
        assert "not found" in resp.json()["detail"]


class TestWorkflowEndpoints:
    def test_complete_approval_workflow(self, test_client):
        feature_name = "integration:workflow:v1"
        test_client.post(
            "/create_feature_metadata",
            json={
                "feature_name": feature_name,
                "feature_type": "batch",
                "feature_data_type": "double",
                "query": "SELECT revenue FROM sales",
                "description": "Workflow test feature",
                "created_by": "developer",
                "user_role": "developer",
            },
        )
        test_client.post(
            "/submit_test_feature_metadata",
            json={
                "feature_name": feature_name,
                "submitted_by": "developer",
                "user_role": "developer",
            },
        )
        test_client.post(
            "/test_feature_metadata",
            json={
                "feature_name": feature_name,
                "test_result": "TEST_SUCCEEDED",
                "tested_by": "test_system",
                "user_role": "tester",
                "test_notes": "All validations passed",
            },
        )
        resp = test_client.post(
            "/approve_feature_metadata",
            json={
                "feature_name": feature_name,
                "approved_by": "approver",
                "user_role": "approver",
                "approval_notes": "Approved for production",
            },
        )
        assert resp.status_code == 200
        assert resp.json()["metadata"]["status"] == "DEPLOYED"

    def test_failure_and_fix_workflow(self, test_client):
        feature_name = "integration:failure:v1"
        test_client.post(
            "/create_feature_metadata",
            json={
                "feature_name": feature_name,
                "feature_type": "real-time",
                "feature_data_type": "boolean",
                "query": "SELECT is_active FROM users",
                "description": "Failure test feature",
                "created_by": "developer",
                "user_role": "developer",
            },
        )
        test_client.post(
            "/submit_test_feature_metadata",
            json={
                "feature_name": feature_name,
                "submitted_by": "developer",
                "user_role": "developer",
            },
        )
        test_client.post(
            "/test_feature_metadata",
            json={
                "feature_name": feature_name,
                "test_result": "TEST_FAILED",
                "tested_by": "test_system",
                "user_role": "tester",
                "test_notes": "Schema validation failed",
            },
        )


class TestRetrievalEndpoints:
    def test_get_feature_metadata(self, test_client):
        feature_name = "integration:retrieve:v1"
        test_client.post(
            "/create_feature_metadata",
            json={
                "feature_name": feature_name,
                "feature_type": "batch",
                "feature_data_type": "bigint",
                "query": "SELECT user_id FROM table",
                "description": "Retrieve test feature",
                "created_by": "developer",
                "user_role": "developer",
            },
        )
        resp = test_client.post(
            "/get_feature_metadata",
            json={"features": feature_name, "user_role": "developer"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["values"]["feature_name"] == feature_name
        assert data["values"]["feature_type"] == "batch"

    def test_get_all_feature_metadata(self, test_client):
        for i in range(3):
            test_client.post(
                "/create_feature_metadata",
                json={
                    "feature_name": f"integration:all:v{i}",
                    "feature_type": "batch",
                    "feature_data_type": "float",
                    "query": f"SELECT value_{i} FROM table",
                    "description": f"All metadata test {i}",
                    "created_by": "developer",
                    "user_role": "developer",
                },
            )
        resp = test_client.post(
            "/get_all_feature_metadata", json={"user_role": "developer"}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "metadata" in data
        assert data["total_count"] >= 3


class TestHealthEndpoint:
    def test_health_check(self, test_client):
        resp = test_client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
