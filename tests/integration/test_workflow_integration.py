import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app


# Temporary data directory fixture
@pytest.fixture
def temp_data_dir():
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


# Test client fixture with temp data
@pytest.fixture
def test_client(temp_data_dir, monkeypatch):
    from app.services import feature_service

    orig_init = feature_service.FeatureMetadataService.__init__

    def custom_init(self, metadata_file=None):
        file_path = temp_data_dir / "test_metadata.json"
        lock_path = temp_data_dir / "test_lock.lock"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        if not file_path.exists():
            file_path.write_text("{}")
        orig_init(self, str(file_path))
        if hasattr(self, "lock_file"):
            self.lock_file = str(lock_path)

    monkeypatch.setattr(feature_service.FeatureMetadataService, "__init__", custom_init)
    if hasattr(app.state, "feature_metadata_service"):
        delattr(app.state, "feature_metadata_service")
    if "feature_metadata_service" in app.__dict__:
        del app.__dict__["feature_metadata_service"]
    with TestClient(app) as client:
        yield client


class TestWorkflowIntegration:
    """Test workflow integration."""

    # Test full feature lifecycle
    def test_complete_feature_lifecycle(self, test_client):
        feature_name = "workflow:lifecycle:v1"
        resp = test_client.post(
            "/create_feature_metadata",
            json={
                "feature_name": feature_name,
                "feature_type": "batch",
                "feature_data_type": "float",
                "query": "SELECT value FROM table",
                "description": "Workflow test feature",
                "created_by": "developer",
                "user_role": "developer",
            },
        )
        assert resp.status_code == 201, resp.text
        data = resp.json()
        assert data["metadata"]["status"] == "DRAFT"
        resp = test_client.post(
            "/ready_test_feature_metadata",
            json={
                "feature_name": feature_name,
                "submitted_by": "developer",
                "user_role": "developer",
            },
        )
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["metadata"]["status"] == "READY_FOR_TESTING"
        resp = test_client.post(
            "/test_feature_metadata",
            json={
                "feature_name": feature_name,
                "test_result": "TEST_SUCCEEDED",
                "tested_by": "test_system",
                "user_role": "external_testing_system",
                "test_notes": "All tests passed",
            },
        )
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["metadata"]["status"] == "TEST_SUCCEEDED"
        resp = test_client.post(
            "/approve_feature_metadata",
            json={
                "feature_name": feature_name,
                "approved_by": "approver",
                "user_role": "approver",
                "approval_notes": "Approved for production",
            },
        )
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["metadata"]["status"] == "DEPLOYED"
        resp = test_client.get("/get_deployed_features")
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert feature_name in data["features"]

    # Test workflow with failure
    def test_testing_failure_workflow(self, test_client):
        feature_name = "workflow:fail:v1"
        resp = test_client.post(
            "/create_feature_metadata",
            json={
                "feature_name": feature_name,
                "feature_type": "batch",
                "feature_data_type": "float",
                "query": "SELECT value FROM table",
                "description": "Workflow test feature",
                "created_by": "developer",
                "user_role": "developer",
            },
        )
        assert resp.status_code == 201, resp.text
        resp = test_client.post(
            "/ready_test_feature_metadata",
            json={
                "feature_name": feature_name,
                "submitted_by": "developer",
                "user_role": "developer",
            },
        )
        assert resp.status_code == 200, resp.text
        resp = test_client.post(
            "/test_feature_metadata",
            json={
                "feature_name": feature_name,
                "test_result": "TEST_FAILED",
                "tested_by": "test_system",
                "user_role": "external_testing_system",
                "test_notes": "Tests failed due to data quality issues",
            },
        )
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["metadata"]["status"] == "TEST_FAILED"
        resp = test_client.post(
            "/fix_feature_metadata",
            json={
                "feature_name": feature_name,
                "fixed_by": "developer",
                "user_role": "developer",
                "fix_description": "Fixed data quality issues",
            },
        )
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["metadata"]["status"] == "DRAFT"
        resp = test_client.post(
            "/ready_test_feature_metadata",
            json={
                "feature_name": feature_name,
                "submitted_by": "developer",
                "user_role": "developer",
            },
        )
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["metadata"]["status"] == "READY_FOR_TESTING"

    # Test workflow with rejection
    def test_rejection_workflow(self, test_client):
        feature_name = "workflow:reject:v1"
        resp = test_client.post(
            "/create_feature_metadata",
            json={
                "feature_name": feature_name,
                "feature_type": "batch",
                "feature_data_type": "float",
                "query": "SELECT value FROM table",
                "description": "Workflow test feature",
                "created_by": "developer",
                "user_role": "developer",
            },
        )
        assert resp.status_code == 201, resp.text
        resp = test_client.post(
            "/ready_test_feature_metadata",
            json={
                "feature_name": feature_name,
                "submitted_by": "developer",
                "user_role": "developer",
            },
        )
        assert resp.status_code == 200, resp.text
        resp = test_client.post(
            "/test_feature_metadata",
            json={
                "feature_name": feature_name,
                "test_result": "TEST_SUCCEEDED",
                "tested_by": "test_system",
                "user_role": "external_testing_system",
            },
        )
        assert resp.status_code == 200, resp.text
        resp = test_client.post(
            "/reject_feature_metadata",
            json={
                "feature_name": feature_name,
                "rejected_by": "approver",
                "user_role": "approver",
                "rejection_reason": "Feature does not meet requirements",
            },
        )
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["metadata"]["status"] == "REJECTED"
        resp = test_client.get("/get_deployed_features")
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert feature_name not in data["features"]
