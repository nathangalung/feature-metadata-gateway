from concurrent.futures import ThreadPoolExecutor

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="class")
def test_client():
    with TestClient(app) as client:
        yield client


class TestConcurrentLoad:
    """Test concurrent load handling."""

    @pytest.fixture(autouse=True)
    def setup(self, test_client):
        self.client = test_client

    # Concurrent create metadata
    def test_concurrent_create_metadata(self):
        def create_feature(idx):
            return self.client.post(
                "/create_feature_metadata",
                json={
                    "feature_name": f"concurrent:load{idx}:v1",
                    "feature_type": "batch",
                    "feature_data_type": "float",
                    "query": f"SELECT value_{idx} FROM table",
                    "description": f"Concurrent test feature {idx}",
                    "created_by": "test_user",
                    "user_role": "developer",
                },
            )

        with ThreadPoolExecutor(max_workers=10) as executor:
            responses = list(executor.map(create_feature, range(10)))
        assert sum(1 for r in responses if r.status_code == 201) > 0

    # Concurrent get all metadata
    def test_concurrent_get_all_metadata(self):
        def get_all_features():
            return self.client.post(
                "/get_all_feature_metadata", json={"user_role": "developer"}
            )

        with ThreadPoolExecutor(max_workers=10) as executor:
            responses = list(executor.map(lambda _: get_all_features(), range(10)))
        assert sum(1 for r in responses if r.status_code == 200) > 0

    # Health check under load
    def test_health_check_under_load(self):
        def health_check():
            return self.client.post("/health")

        with ThreadPoolExecutor(max_workers=5) as executor:
            responses = list(executor.map(lambda _: health_check(), range(5)))
        assert all(r.status_code == 200 for r in responses)
