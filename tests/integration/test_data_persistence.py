import json
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


class TestDataPersistence:
    """Test data persistence."""

    # Test create and retrieve
    def test_create_and_retrieve_persisted_data(self, test_client, temp_data_dir):
        resp = test_client.post(
            "/create_feature_metadata",
            json={
                "feature_name": "persistence:test:v1",
                "feature_type": "batch",
                "feature_data_type": "float",
                "query": "SELECT value FROM table",
                "description": "Persistence test feature",
                "created_by": "test_user",
                "user_role": "developer",
            },
        )
        assert resp.status_code == 201
        metadata_file = temp_data_dir / "test_metadata.json"
        assert metadata_file.exists()
        with open(metadata_file) as f:
            stored_data = json.load(f)
        assert "persistence:test:v1" in stored_data
        assert stored_data["persistence:test:v1"]["feature_type"] == "batch"
        assert stored_data["persistence:test:v1"]["feature_data_type"] == "float"
        assert (
            stored_data["persistence:test:v1"]["description"]
            == "Persistence test feature"
        )

    # Test update is persisted
    def test_update_persisted_data(self, test_client, temp_data_dir):
        test_client.post(
            "/create_feature_metadata",
            json={
                "feature_name": "persistence:update:v1",
                "feature_type": "batch",
                "feature_data_type": "float",
                "query": "SELECT value FROM table",
                "description": "Original description",
                "created_by": "test_user",
                "user_role": "developer",
            },
        )
        test_client.post(
            "/update_feature_metadata",
            json={
                "feature_name": "persistence:update:v1",
                "description": "Updated description",
                "last_updated_by": "test_user",
                "user_role": "developer",
            },
        )
        metadata_file = temp_data_dir / "test_metadata.json"
        assert metadata_file.exists()
        with open(metadata_file) as f:
            stored_data = json.load(f)
        assert (
            stored_data["persistence:update:v1"]["description"] == "Updated description"
        )

    # Test restart loads data
    def test_restart_with_persisted_data(self, test_client, temp_data_dir):
        test_client.post(
            "/create_feature_metadata",
            json={
                "feature_name": "persistence:restart:v1",
                "feature_type": "batch",
                "feature_data_type": "float",
                "query": "SELECT value FROM table",
                "description": "Restart test feature",
                "created_by": "test_user",
                "user_role": "developer",
            },
        )
        from app.services.feature_service import FeatureMetadataService

        new_service = FeatureMetadataService(str(temp_data_dir / "test_metadata.json"))
        if hasattr(new_service, "lock_file"):
            new_service.lock_file = str(temp_data_dir / "test_lock.lock")
        if hasattr(new_service, "load_metadata"):
            new_service.load_metadata()
        else:
            with open(new_service.metadata_file) as f:
                new_service.metadata = json.load(f)
        assert "persistence:restart:v1" in new_service.metadata
        assert (
            new_service.metadata["persistence:restart:v1"]["description"]
            == "Restart test feature"
        )

    # Test delete is persisted
    def test_delete_feature_persistence(self, test_client, temp_data_dir):
        test_client.post(
            "/create_feature_metadata",
            json={
                "feature_name": "persistence:delete:v1",
                "feature_type": "batch",
                "feature_data_type": "float",
                "query": "SELECT value FROM table",
                "description": "Delete test feature",
                "created_by": "test_user",
                "user_role": "developer",
            },
        )
        test_client.post(
            "/delete_feature_metadata",
            json={
                "feature_name": "persistence:delete:v1",
                "deleted_by": "test_user",
                "user_role": "developer",
                "deletion_reason": "Testing deletion",
            },
        )
        metadata_file = temp_data_dir / "test_metadata.json"
        assert metadata_file.exists()
        with open(metadata_file) as f:
            stored_data = json.load(f)
        assert stored_data["persistence:delete:v1"]["status"] == "DELETED"
        assert "deleted_by" in stored_data["persistence:delete:v1"]
