# import json
# import tempfile
# from pathlib import Path

# import pytest
# from fastapi.testclient import TestClient

# from app.main import app, feature_metadata_service

# @pytest.fixture
# def test_client(temp_data_dir):
#     with TestClient(app) as client:
#         # Wait for lifespan to initialize feature_metadata_service
#         import time
#         for _ in range(10):
#             if feature_metadata_service is not None:
#                 break
#             time.sleep(0.1)
#         original_metadata_file = feature_metadata_service.metadata_file
#         original_lock_file = getattr(feature_metadata_service, "lock_file", None)
#         feature_metadata_service.metadata_file = temp_data_dir / "test_metadata.json"
#         if hasattr(feature_metadata_service, "lock_file"):
#             feature_metadata_service.lock_file = temp_data_dir / "test_lock.lock"
#         feature_metadata_service.metadata = {}
#         yield client
#         feature_metadata_service.metadata_file = original_metadata_file
#         if original_lock_file:
#             feature_metadata_service.lock_file = original_lock_file

# @pytest.fixture
# def temp_data_dir():
#     with tempfile.TemporaryDirectory() as temp_dir:
#         yield Path(temp_dir)

# class TestDataPersistence:
#     """Test data persistence."""

#     def test_create_and_retrieve_persisted_data(self, test_client, temp_data_dir):
#         """Test create and retrieve data."""
#         resp = test_client.post("/create_feature_metadata", json={
#             "feature_name": "persistence:test:v1",
#             "feature_type": "batch",
#             "feature_data_type": "float",
#             "query": "SELECT value FROM table",
#             "description": "Persistence test feature",
#             "created_by": "test_user",
#             "user_role": "developer"
#         })
#         assert resp.status_code == 201
#         metadata_file = temp_data_dir / "test_metadata.json"
#         assert metadata_file.exists()
#         with open(metadata_file) as f:
#             stored_data = json.load(f)
#         assert "persistence:test:v1" in stored_data
#         assert stored_data["persistence:test:v1"]["feature_type"] == "batch"
#         assert stored_data["persistence:test:v1"]["feature_data_type"] == "float"
#         assert stored_data["persistence:test:v1"]["description"] == "Persistence test feature"

#     def test_update_persisted_data(self, test_client, temp_data_dir):
#         """Test update is persisted."""
#         test_client.post("/create_feature_metadata", json={
#             "feature_name": "persistence:update:v1",
#             "feature_type": "batch",
#             "feature_data_type": "float",
#             "query": "SELECT value FROM table",
#             "description": "Original description",
#             "created_by": "test_user",
#             "user_role": "developer"
#         })
#         test_client.post("/update_feature_metadata", json={
#             "feature_name": "persistence:update:v1",
#             "description": "Updated description",
#             "last_updated_by": "test_user",
#             "user_role": "developer"
#         })
#         metadata_file = temp_data_dir / "test_metadata.json"
#         with open(metadata_file) as f:
#             stored_data = json.load(f)
#         assert stored_data["persistence:update:v1"]["description"] == "Updated description"

#     def test_restart_with_persisted_data(self, test_client, temp_data_dir):
#         """Test restart loads data."""
#         test_client.post("/create_feature_metadata", json={
#             "feature_name": "persistence:restart:v1",
#             "feature_type": "batch",
#             "feature_data_type": "float",
#             "query": "SELECT value FROM table",
#             "description": "Restart test feature",
#             "created_by": "test_user",
#             "user_role": "developer"
#         })
#         new_service = feature_metadata_service.__class__()
#         new_service.metadata_file = temp_data_dir / "test_metadata.json"
#         if hasattr(new_service, "lock_file"):
#             new_service.lock_file = temp_data_dir / "test_lock.lock"
#         assert "persistence:restart:v1" in new_service.metadata
#         assert new_service.metadata["persistence:restart:v1"]["description"] == "Restart test feature"

#     def test_delete_feature_persistence(self, test_client, temp_data_dir):
#         """Test delete is persisted."""
#         test_client.post("/create_feature_metadata", json={
#             "feature_name": "persistence:delete:v1",
#             "feature_type": "batch",
#             "feature_data_type": "float",
#             "query": "SELECT value FROM table",
#             "description": "Delete test feature",
#             "created_by": "test_user",
#             "user_role": "developer"
#         })
#         test_client.post("/delete_feature_metadata", json={
#             "feature_name": "persistence:delete:v1",
#             "deleted_by": "test_user",
#             "user_role": "developer",
#             "deletion_reason": "Testing deletion"
#         })
#         metadata_file = temp_data_dir / "test_metadata.json"
#         with open(metadata_file) as f:
#             stored_data = json.load(f)
#         assert stored_data["persistence:delete:v1"]["status"] == "DELETED"
#         assert "deleted_by" in stored_data["persistence:delete:v1"]
#         assert "deletion_reason" in stored_data["persistence:delete:v1"]
