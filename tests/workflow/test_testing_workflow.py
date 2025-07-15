import pytest
from fastapi.testclient import TestClient

from app.main import app


class TestTestingWorkflow:
    """Testing workflow tests."""

    @pytest.fixture(autouse=True)
    def setup(self):
        with TestClient(app) as client:
            self.client = client
            yield

    # Test passed workflow
    def test_successful_testing_workflow(self):
        feature_name = "testing:success:v1"
        resp = self.client.post(
            "/create_feature_metadata",
            json={
                "feature_name": feature_name,
                "feature_type": "batch",
                "feature_data_type": "float",
                "query": "SELECT value FROM test_table",
                "description": "Testing workflow test",
                "created_by": "dev_user",
                "user_role": "developer",
            },
        )
        assert resp.status_code in (200, 201), resp.text
        resp = self.client.post(
            "/submit_test_feature_metadata",
            json={
                "feature_name": feature_name,
                "submitted_by": "dev_user",
                "user_role": "developer",
            },
        )
        assert resp.status_code == 200, resp.text
        metadata = resp.json()["metadata"]
        assert metadata["status"] == "READY_FOR_TESTING"
        assert metadata["submitted_by"] == "dev_user"
        resp = self.client.post(
            "/test_feature_metadata",
            json={
                "feature_name": feature_name,
                "test_result": "TEST_SUCCEEDED",
                "tested_by": "test_system",
                "user_role": "tester",
                "test_notes": "All tests passed successfully",
            },
        )
        assert resp.status_code == 200, resp.text
        metadata = resp.json()["metadata"]
        assert metadata["status"] == "TEST_SUCCEEDED"
        assert metadata["tested_by"] == "test_system"
        assert metadata["test_notes"] == "All tests passed successfully"

    # Test failed workflow
    def test_failed_testing_workflow(self):
        feature_name = "testing:failure:v1"
        resp = self.client.post(
            "/create_feature_metadata",
            json={
                "feature_name": feature_name,
                "feature_type": "batch",
                "feature_data_type": "float",
                "query": "SELECT value FROM test_table",
                "description": "Testing failure workflow test",
                "created_by": "dev_user",
                "user_role": "developer",
            },
        )
        assert resp.status_code in (200, 201), resp.text
        resp = self.client.post(
            "/submit_test_feature_metadata",
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
                "test_result": "TEST_FAILED",
                "tested_by": "test_system",
                "user_role": "tester",
                "test_notes": "Performance requirements not met",
            },
        )
        assert resp.status_code == 200, resp.text
        metadata = resp.json()["metadata"]
        assert metadata["status"] == "TEST_FAILED"
        assert metadata["test_notes"] == "Performance requirements not met"

    # Test role restrictions
    def test_testing_permission_restrictions(self):
        feature_name = "testing:permissions:v1"
        resp = self.client.post(
            "/create_feature_metadata",
            json={
                "feature_name": feature_name,
                "feature_type": "batch",
                "feature_data_type": "float",
                "query": "SELECT value FROM test_table",
                "description": "Testing permissions test",
                "created_by": "dev_user",
                "user_role": "developer",
            },
        )
        assert resp.status_code in (200, 201), resp.text
        resp = self.client.post(
            "/submit_test_feature_metadata",
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
                "tested_by": "dev_user",
                "user_role": "developer",
            },
        )
        assert resp.status_code in (400, 422), resp.text
        resp = self.client.post(
            "/test_feature_metadata",
            json={
                "feature_name": feature_name,
                "test_result": "TEST_SUCCEEDED",
                "tested_by": "approver_user",
                "user_role": "approver",
            },
        )
        assert resp.status_code in (400, 422), resp.text
        resp = self.client.post(
            "/test_feature_metadata",
            json={
                "feature_name": feature_name,
                "test_result": "TEST_SUCCEEDED",
                "tested_by": "test_system",
                "user_role": "tester",
            },
        )
        assert resp.status_code == 200, resp.text

    # Test non-existent feature
    def test_non_existent_feature_testing(self):
        resp = self.client.post(
            "/submit_test_feature_metadata",
            json={
                "feature_name": "nonexistent:feature:v1",
                "submitted_by": "dev_user",
                "user_role": "developer",
            },
        )
        assert resp.status_code in (400, 404, 422), resp.text
        if resp.status_code in (400, 404):
            assert "not found" in resp.json()["detail"].lower()
        resp = self.client.post(
            "/test_feature_metadata",
            json={
                "feature_name": "nonexistent:feature:v1",
                "test_result": "TEST_SUCCEEDED",
                "tested_by": "test_system",
                "user_role": "tester",
            },
        )
        assert resp.status_code in (400, 404, 422), resp.text
        if resp.status_code in (400, 404):
            assert "not found" in resp.json()["detail"].lower()
