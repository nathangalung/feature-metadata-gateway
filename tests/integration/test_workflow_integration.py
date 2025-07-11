# import pytest
# from fastapi.testclient import TestClient

# from app.main import app


# class TestWorkflowIntegration:
#     """Test workflow integration."""

#     @pytest.fixture(autouse=True)
#     def setup(self):
#         """Setup test client."""
#         self.client = TestClient(app)

#     def test_complete_feature_lifecycle(self):
#         """Test full feature lifecycle."""
#         feature_name = "workflow:lifecycle:v1"
#         resp = self.client.post("/create_feature_metadata", json={
#             "feature_name": feature_name,
#             "feature_type": "batch",
#             "feature_data_type": "float",
#             "query": "SELECT value FROM table",
#             "description": "Workflow test feature",
#             "created_by": "developer",
#             "user_role": "developer"
#         })
#         assert resp.status_code == 201
#         data = resp.json()
#         assert data["metadata"]["status"] == "DRAFT"
#         resp = self.client.post("/ready_test_feature_metadata", json={
#             "feature_name": feature_name,
#             "submitted_by": "developer",
#             "user_role": "developer"
#         })
#         assert resp.status_code == 200
#         data = resp.json()
#         assert data["metadata"]["status"] == "READY_FOR_TESTING"
#         resp = self.client.post("/test_feature_metadata", json={
#             "feature_name": feature_name,
#             "test_result": "TEST_SUCCEEDED",
#             "tested_by": "test_system",
#             "user_role": "external_testing_system",
#             "test_notes": "All tests passed"
#         })
#         assert resp.status_code == 200
#         data = resp.json()
#         assert data["metadata"]["status"] == "TEST_SUCCEEDED"
#         resp = self.client.post("/approve_feature_metadata", json={
#             "feature_name": feature_name,
#             "approved_by": "approver",
#             "user_role": "approver",
#             "approval_notes": "Approved for production"
#         })
#         assert resp.status_code == 200
#         data = resp.json()
#         assert data["metadata"]["status"] == "DEPLOYED"
#         resp = self.client.get("/get_deployed_features")
#         assert resp.status_code == 200
#         data = resp.json()
#         assert feature_name in data["features"]

#     def test_testing_failure_workflow(self):
#         """Test workflow with failure."""
#         feature_name = "workflow:fail:v1"
#         self.client.post("/create_feature_metadata", json={
#             "feature_name": feature_name,
#             "feature_type": "batch",
#             "feature_data_type": "float",
#             "query": "SELECT value FROM table",
#             "description": "Workflow test feature",
#             "created_by": "developer",
#             "user_role": "developer"
#         })
#         self.client.post("/ready_test_feature_metadata", json={
#             "feature_name": feature_name,
#             "submitted_by": "developer",
#             "user_role": "developer"
#         })
#         resp = self.client.post("/test_feature_metadata", json={
#             "feature_name": feature_name,
#             "test_result": "TEST_FAILED",
#             "tested_by": "test_system",
#             "user_role": "external_testing_system",
#             "test_notes": "Tests failed due to data quality issues"
#         })
#         assert resp.status_code == 200
#         data = resp.json()
#         assert data["metadata"]["status"] == "TEST_FAILED"
#         resp = self.client.post("/fix_feature_metadata", json={
#             "feature_name": feature_name,
#             "fixed_by": "developer",
#             "user_role": "developer",
#             "fix_description": "Fixed data quality issues"
#         })
#         assert resp.status_code == 200
#         data = resp.json()
#         assert data["metadata"]["status"] == "DRAFT"
#         resp = self.client.post("/ready_test_feature_metadata", json={
#             "feature_name": feature_name,
#             "submitted_by": "developer",
#             "user_role": "developer"
#         })
#         assert resp.status_code == 200
#         data = resp.json()
#         assert data["metadata"]["status"] == "READY_FOR_TESTING"

#     def test_rejection_workflow(self):
#         """Test workflow with rejection."""
#         feature_name = "workflow:reject:v1"
#         self.client.post("/create_feature_metadata", json={
#             "feature_name": feature_name,
#             "feature_type": "batch",
#             "feature_data_type": "float",
#             "query": "SELECT value FROM table",
#             "description": "Workflow test feature",
#             "created_by": "developer",
#             "user_role": "developer"
#         })
#         self.client.post("/ready_test_feature_metadata", json={
#             "feature_name": feature_name,
#             "submitted_by": "developer",
#             "user_role": "developer"
#         })
#         self.client.post("/test_feature_metadata", json={
#             "feature_name": feature_name,
#             "test_result": "TEST_SUCCEEDED",
#             "tested_by": "test_system",
#             "user_role": "external_testing_system"
#         })
#         assert resp.status_code == 200
#         data = resp.json()
#         assert data["metadata"]["status"] == "TEST_FAILED"
#         resp = self.client.get("/get_deployed_features")
#         assert resp.status_code == 200
#         data = resp.json()
#         assert feature_name not in data["features"]
