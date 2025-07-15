import time

import pytest
from fastapi.testclient import TestClient

from app.main import app


class TestResponseTimes:
    @pytest.fixture(autouse=True)
    def setup(self):
        with TestClient(app) as client:
            self.client = client
            yield

    def test_create_feature_response_time(self):
        start = time.time()
        resp = self.client.post(
            "/create_feature_metadata",
            json={
                "feature_name": "perf:create:v1",
                "feature_type": "real-time",
                "feature_data_type": "float",
                "query": "SELECT score FROM model",
                "description": "Performance test",
                "created_by": "perf_user",
                "user_role": "developer",
            },
        )
        end = time.time()
        duration = end - start
        assert resp.status_code == 201
        assert duration < 5, f"Create took {duration:.2f}s"

    def test_get_metadata_response_time(self):
        self.client.post(
            "/create_feature_metadata",
            json={
                "feature_name": "perf:get:v1",
                "feature_type": "batch",
                "feature_data_type": "int",
                "query": "SELECT count FROM table",
                "description": "Get performance test",
                "created_by": "perf_user",
                "user_role": "developer",
            },
        )
        start = time.time()
        resp = self.client.post(
            "/get_feature_metadata",
            json={"features": "perf:get:v1", "user_role": "developer"},
        )
        end = time.time()
        duration = end - start
        assert resp.status_code == 200
        assert duration < 5, f"Get took {duration:.2f}s"

    def test_update_feature_response_time(self):
        self.client.post(
            "/create_feature_metadata",
            json={
                "feature_name": "perf:update:v1",
                "feature_type": "compute-first",
                "feature_data_type": "decimal",
                "query": "SELECT price FROM products",
                "description": "Update performance test",
                "created_by": "perf_user",
                "user_role": "developer",
            },
        )
        start = time.time()
        resp = self.client.post(
            "/update_feature_metadata",
            json={
                "feature_name": "perf:update:v1",
                "description": "Updated for performance test",
                "last_updated_by": "perf_user",
                "user_role": "developer",
            },
        )
        end = time.time()
        duration = end - start
        assert resp.status_code == 200
        assert duration < 5, f"Update took {duration:.2f}s"

    def test_workflow_operation_response_time(self):
        feature_name = "perf:workflow:v1"
        self.client.post(
            "/create_feature_metadata",
            json={
                "feature_name": feature_name,
                "feature_type": "batch",
                "feature_data_type": "string",
                "query": "SELECT name FROM users",
                "description": "Workflow performance test",
                "created_by": "perf_user",
                "user_role": "developer",
            },
        )
        start = time.time()
        resp = self.client.post(
            "/submit_test_feature_metadata",
            json={
                "feature_name": feature_name,
                "submitted_by": "perf_user",
                "user_role": "developer",
            },
        )
        end = time.time()
        duration = end - start
        assert resp.status_code == 200
        assert duration < 5, f"Workflow took {duration:.2f}s"
