"""Test feature testing workflow."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


class TestTestingWorkflow:
    """Test feature testing workflow."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test client with lifespan."""
        with TestClient(app) as client:
            self.client = client
            yield

    def test_successful_testing_workflow(self):
        """Test successful testing workflow."""
        feature_name = "testing:success:v1"
        # Create feature
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
        # Ready for testing
        resp = self.client.post(
            "/ready_test_feature_metadata",
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
        # Pass testing
        resp = self.client.post(
            "/test_feature_metadata",
            json={
                "feature_name": feature_name,
                "test_result": "TEST_SUCCEEDED",
                "tested_by": "test_system",
                "user_role": "external_testing_system",
                "test_notes": "All tests passed successfully",
            },
        )
        assert resp.status_code == 200, resp.text
        metadata = resp.json()["metadata"]
        assert metadata["status"] == "TEST_SUCCEEDED"
        assert metadata["tested_by"] == "test_system"
        assert metadata["test_notes"] == "All tests passed successfully"

    def test_failed_testing_workflow(self):
        """Test failed testing workflow."""
        feature_name = "testing:failure:v1"
        # Create feature
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
        # Ready for testing
        resp = self.client.post(
            "/ready_test_feature_metadata",
            json={
                "feature_name": feature_name,
                "submitted_by": "dev_user",
                "user_role": "developer",
            },
        )
        assert resp.status_code == 200, resp.text
        # Fail testing
        resp = self.client.post(
            "/test_feature_metadata",
            json={
                "feature_name": feature_name,
                "test_result": "TEST_FAILED",
                "tested_by": "test_system",
                "user_role": "external_testing_system",
                "test_notes": "Performance requirements not met",
            },
        )
        assert resp.status_code == 200, resp.text
        metadata = resp.json()["metadata"]
        assert metadata["status"] == "TEST_FAILED"
        assert metadata["test_notes"] == "Performance requirements not met"
        # Fix feature
        resp = self.client.post(
            "/fix_feature_metadata",
            json={
                "feature_name": feature_name,
                "fixed_by": "dev_user",
                "user_role": "developer",
                "fix_description": "Optimized query performance",
            },
        )
        assert resp.status_code == 200, resp.text
        metadata = resp.json()["metadata"]
        assert metadata["status"] == "DRAFT"
        assert metadata["tested_by"] is None
        assert metadata["tested_time"] is None
        assert metadata["fix_description"] == "Optimized query performance"

    def test_testing_permission_restrictions(self):
        """Test role permission restrictions."""
        feature_name = "testing:permissions:v1"
        # Create feature
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
        # Ready for testing
        resp = self.client.post(
            "/ready_test_feature_metadata",
            json={
                "feature_name": feature_name,
                "submitted_by": "dev_user",
                "user_role": "developer",
            },
        )
        assert resp.status_code == 200, resp.text
        # Test with developer role (fail)
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
        # Test with approver role (fail)
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
        # Test with correct role
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

    def test_non_existent_feature_testing(self):
        """Test non-existent feature testing."""
        # Ready for testing (fail)
        resp = self.client.post(
            "/ready_test_feature_metadata",
            json={
                "feature_name": "nonexistent:feature:v1",
                "submitted_by": "dev_user",
                "user_role": "developer",
            },
        )
        assert resp.status_code in (400, 404, 422), resp.text
        if resp.status_code in (400, 404):
            assert "not found" in resp.json()["detail"].lower()
        # Test non-existent feature (fail)
        resp = self.client.post(
            "/test_feature_metadata",
            json={
                "feature_name": "nonexistent:feature:v1",
                "test_result": "TEST_SUCCEEDED",
                "tested_by": "test_system",
                "user_role": "external_testing_system",
            },
        )
        assert resp.status_code in (400, 404, 422), resp.text
        if resp.status_code in (400, 404):
            assert "not found" in resp.json()["detail"].lower()
