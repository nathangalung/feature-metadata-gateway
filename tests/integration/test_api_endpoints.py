# """Integration tests for API endpoints."""

# import pytest
# from fastapi.testclient import TestClient

# from app.main import app

# @pytest.fixture
# def test_client():
#     with TestClient(app) as client:
#         yield client

# class TestFeatureCreationEndpoints:
#     """Test feature creation endpoints."""

#     def test_create_feature_success(self, test_client):
#         """Test create feature success."""
#         response = test_client.post("/create_feature_metadata", json={
#             "feature_name": "integration:create:v1",
#             "feature_type": "batch",
#             "feature_data_type": "float",
#             "query": "SELECT value FROM table",
#             "description": "Integration test feature",
#             "created_by": "integration_user",
#             "user_role": "developer"
#         })
#         assert response.status_code == 201
#         data = response.json()
#         assert data["metadata"]["feature_name"] == "integration:create:v1"
#         assert data["metadata"]["status"] == "DRAFT"

#     def test_create_duplicate_feature_error(self, test_client):
#         """Test duplicate feature error."""
#         feature_data = {
#             "feature_name": "integration:duplicate:v1",
#             "feature_type": "batch",
#             "feature_data_type": "int",
#             "query": "SELECT count FROM table",
#             "description": "Duplicate test",
#             "created_by": "integration_user",
#             "user_role": "developer"
#         }
#         response1 = test_client.post("/create_feature_metadata", json=feature_data)
#         assert response1.status_code == 201
#         response2 = test_client.post("/create_feature_metadata", json=feature_data)
#         assert response2.status_code == 400
#         assert "already exists" in response2.json()["detail"]

#     def test_create_feature_invalid_data(self, test_client):
#         """Test create feature invalid data."""
#         response = test_client.post("/create_feature_metadata", json={
#             "feature_name": "invalid_name_format",
#             "feature_type": "invalid_type",
#             "feature_data_type": "invalid_data_type",
#             "query": "SELECT 1",
#             "description": "Invalid test",
#             "created_by": "user",
#             "user_role": "invalid_role"
#         })
#         assert response.status_code == 400

# class TestFeatureUpdateEndpoints:
#     """Test feature update endpoints."""

#     def test_update_feature_description(self, test_client):
#         """Test update feature description."""
#         create_response = test_client.post("/create_feature_metadata", json={
#             "feature_name": "integration:update:v1",
#             "feature_type": "real-time",
#             "feature_data_type": "string",
#             "query": "SELECT name FROM users",
#             "description": "Original description",
#             "created_by": "integration_user",
#             "user_role": "developer"
#         })
#         assert create_response.status_code == 201
#         update_response = test_client.post("/update_feature_metadata", json={
#             "feature_name": "integration:update:v1",
#             "description": "Updated description",
#             "last_updated_by": "integration_user",
#             "user_role": "developer"
#         })
#         assert update_response.status_code == 200
#         data = update_response.json()
#         assert data["metadata"]["description"] == "Updated description"
#         assert data["metadata"]["last_updated_by"] == "integration_user"

#     def test_update_nonexistent_feature(self, test_client):
#         """Test update nonexistent feature."""
#         response = test_client.post("/update_feature_metadata", json={
#             "feature_name": "integration:nonexistent:v1",
#             "description": "New description",
#             "last_updated_by": "user",
#             "user_role": "developer"
#         })
#         assert response.status_code == 400
#         assert "not found" in response.json()["detail"]

# class TestWorkflowEndpoints:
#     """Test workflow endpoints."""

#     def test_complete_approval_workflow(self, test_client):
#         """Test complete approval workflow."""
#         feature_name = "integration:workflow:v1"
#         create_response = test_client.post("/create_feature_metadata", json={
#             "feature_name": feature_name,
#             "feature_type": "batch",
#             "feature_data_type": "double",
#             "query": "SELECT revenue FROM sales",
#             "description": "Workflow test feature",
#             "created_by": "developer",
#             "user_role": "developer"
#         })
#         assert create_response.status_code == 201
#         assert create_response.json()["metadata"]["status"] == "DRAFT"
#         ready_response = test_client.post("/ready_test_feature_metadata", json={
#             "feature_name": feature_name,
#             "submitted_by": "developer",
#             "user_role": "developer"
#         })
#         assert ready_response.status_code == 200
#         assert ready_response.json()["metadata"]["status"] == "READY_FOR_TESTING"
#         test_response = test_client.post("/test_feature_metadata", json={
#             "feature_name": feature_name,
#             "test_result": "TEST_SUCCEEDED",
#             "tested_by": "test_system",
#             "user_role": "external_testing_system",
#             "test_notes": "All validations passed"
#         })
#         assert test_response.status_code == 200
#         assert test_response.json()["metadata"]["status"] == "TEST_SUCCEEDED"
#         approve_response = test_client.post("/approve_feature_metadata", json={
#             "feature_name": feature_name,
#             "approved_by": "approver",
#             "user_role": "approver",
#             "approval_notes": "Approved for production"
#         })
#         assert approve_response.status_code == 200
#         assert approve_response.json()["metadata"]["status"] == "DEPLOYED"

#     def test_failure_and_fix_workflow(self, test_client):
#         """Test failure and fix workflow."""
#         feature_name = "integration:failure:v1"
#         test_client.post("/create_feature_metadata", json={
#             "feature_name": feature_name,
#             "feature_type": "real-time",
#             "feature_data_type": "boolean",
#             "query": "SELECT is_active FROM users",
#             "description": "Failure test feature",
#             "created_by": "developer",
#             "user_role": "developer"
#         })
#         test_client.post("/ready_test_feature_metadata", json={
#             "feature_name": feature_name,
#             "submitted_by": "developer",
#             "user_role": "developer"
#         })
#         test_response = test_client.post("/test_feature_metadata", json={
#             "feature_name": feature_name,
#             "test_result": "TEST_FAILED",
#             "tested_by": "test_system",
#             "user_role": "external_testing_system",
#             "test_notes": "Schema validation failed"
#         })
#         assert test_response.status_code == 200
#         assert test_response.json()["metadata"]["status"] == "TEST_FAILED"
#         fix_response = test_client.post("/fix_feature_metadata", json={
#             "feature_name": feature_name,
#             "fixed_by": "developer",
#             "user_role": "developer",
#             "fix_description": "Fixed schema issues"
#         })
#         assert fix_response.status_code == 200
#         assert fix_response.json()["metadata"]["status"] == "DRAFT"

# class TestRetrievalEndpoints:
#     """Test retrieval endpoints."""

#     def test_get_feature_metadata(self, test_client):
#         """Test get feature metadata."""
#         feature_name = "integration:retrieve:v1"
#         test_client.post("/create_feature_metadata", json={
#             "feature_name": feature_name,
#             "feature_type": "batch",
#             "feature_data_type": "bigint",
#             "query": "SELECT user_id FROM table",
#             "description": "Retrieve test feature",
#             "created_by": "developer",
#             "user_role": "developer"
#         })
#         response = test_client.post("/get_feature_metadata", json={
#             "feature_name": feature_name,
#             "user_role": "developer"
#         })
#         assert response.status_code == 200
#         data = response.json()
#         assert data["metadata"]["feature_name"] == feature_name
#         assert data["metadata"]["feature_type"] == "batch"

#     def test_get_all_feature_metadata(self, test_client):
#         """Test get all feature metadata."""
#         for i in range(3):
#             test_client.post("/create_feature_metadata", json={
#                 "feature_name": f"integration:all:v{i}",
#                 "feature_type": "batch",
#                 "feature_data_type": "float",
#                 "query": f"SELECT value_{i} FROM table",
#                 "description": f"All metadata test {i}",
#                 "created_by": "developer",
#                 "user_role": "developer"
#             })
#         response = test_client.post("/get_all_feature_metadata", json={
#             "user_role": "developer"
#         })
#         assert response.status_code == 200
#         data = response.json()
#         assert "metadata" in data
#         assert data["total_count"] >= 3

#     def test_get_deployed_features(self, test_client):
#         """Test get deployed features."""
#         feature_name = "integration:deployed:v1"
#         test_client.post("/create_feature_metadata", json={
#             "feature_name": feature_name,
#             "feature_type": "batch",
#             "feature_data_type": "float",
#             "query": "SELECT value FROM table",
#             "description": "Deployed test feature",
#             "created_by": "developer",
#             "user_role": "developer"
#         })
#         test_client.post("/ready_test_feature_metadata", json={
#             "feature_name": feature_name,
#             "submitted_by": "developer",
#             "user_role": "developer"
#         })
#         test_client.post("/test_feature_metadata", json={
#             "feature_name": feature_name,
#             "test_result": "TEST_SUCCEEDED",
#             "tested_by": "test_system",
#             "user_role": "external_testing_system"
#         })
#         test_client.post("/approve_feature_metadata", json={
#             "feature_name": feature_name,
#             "approved_by": "approver",
#             "user_role": "approver"
#         })
#         response = test_client.get("/get_deployed_features")
#         assert response.status_code == 200
#         data = response.json()
#         assert feature_name in data["features"]

# class TestHealthEndpoint:
#     """Test health endpoint."""

#     def test_health_check(self, test_client):
#         """Test health check."""
#         response = test_client.get("/health")
#         assert response.status_code == 200
#         data = response.json()
#         assert data["status"] == "healthy"