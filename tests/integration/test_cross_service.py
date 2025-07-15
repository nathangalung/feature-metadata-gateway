import pytest
from fastapi.testclient import TestClient

from app.main import app


class TestCrossServiceIntegration:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = TestClient(app)

    def test_feature_metadata_to_feature_service(self):
        resp = self.client.post(
            "/create_feature_metadata",
            json={
                "feature_name": "cross:service:v1",
                "feature_type": "batch",
                "feature_data_type": "float",
                "query": "SELECT value FROM table",
                "description": "Cross service test feature",
                "created_by": "test_user",
                "user_role": "developer",
            },
        )
        assert resp.status_code == 201

    def test_deployed_status_sync(self):
        self.client.post(
            "/create_feature_metadata",
            json={
                "feature_name": "cross:deployed:v1",
                "feature_type": "real-time",
                "feature_data_type": "int",
                "query": "SELECT count FROM table",
                "description": "Cross service deployed test",
                "created_by": "test_user",
                "user_role": "developer",
            },
        )
        self.client.post(
            "/ready_test_feature_metadata",
            json={
                "feature_name": "cross:deployed:v1",
                "submitted_by": "test_user",
                "user_role": "developer",
            },
        )
        self.client.post(
            "/test_feature_metadata",
            json={
                "feature_name": "cross:deployed:v1",
                "test_result": "TEST_SUCCEEDED",
                "tested_by": "test_system",
                "user_role": "tester",
            },
        )
        self.client.post(
            "/approve_feature_metadata",
            json={
                "feature_name": "cross:deployed:v1",
                "approved_by": "approver_user",
                "user_role": "approver",
            },
        )
