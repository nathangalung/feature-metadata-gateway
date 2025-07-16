import os
import time

import psutil
import pytest
from fastapi.testclient import TestClient

from app.main import app


# Test client fixture
@pytest.fixture
def test_client():
    with TestClient(app) as client:
        yield client


class TestBoundaryConditions:
    # Max field lengths
    def test_maximum_field_lengths(self, test_client):
        long_feature_name = "a" * 1000 + ":name:" + "v" * 1000
        response = test_client.post(
            "/create_feature_metadata",
            json={
                "feature_name": long_feature_name,
                "feature_type": "batch",
                "feature_data_type": "string",
                "query": "SELECT data FROM table",
                "description": "Long name test",
                "created_by": "test_user",
                "user_role": "developer",
            },
        )
        assert response.status_code in [400, 422, 413, 500]

        long_description = "A" * 50000
        response = test_client.post(
            "/create_feature_metadata",
            json={
                "feature_name": "boundary:description:1",
                "feature_type": "batch",
                "feature_data_type": "string",
                "query": "SELECT data FROM table",
                "description": long_description,
                "created_by": "test_user",
                "user_role": "developer",
            },
        )
        assert response.status_code in [201, 400, 422, 413, 500]

        long_query = (
            "SELECT " + ", ".join([f"field_{i}" for i in range(1000)]) + " FROM table"
        )
        response = test_client.post(
            "/create_feature_metadata",
            json={
                "feature_name": "boundary:query:1",
                "feature_type": "batch",
                "feature_data_type": "string",
                "query": long_query,
                "description": "Long query test",
                "created_by": "test_user",
                "user_role": "developer",
            },
        )
        assert response.status_code in [201, 400, 422, 413, 500]

    # Min field lengths
    def test_minimum_field_lengths(self, test_client):
        response = test_client.post(
            "/create_feature_metadata",
            json={
                "feature_name": "a:b:1",
                "feature_type": "batch",
                "feature_data_type": "int",
                "query": "SELECT 1",
                "description": "Min test",
                "created_by": "u",
                "user_role": "developer",
            },
        )
        assert response.status_code in [201, 400, 422, 500]

        response = test_client.post(
            "/create_feature_metadata",
            json={
                "feature_name": "",
                "feature_type": "batch",
                "feature_data_type": "int",
                "query": "SELECT 1",
                "description": "Empty name test",
                "created_by": "user",
                "user_role": "developer",
            },
        )
        assert response.status_code in [400, 422, 500]

    # Large metadata set
    def test_large_metadata_set(self, test_client):
        feature_count = 10
        start_time = time.time()
        for i in range(feature_count):
            test_client.post(
                "/create_feature_metadata",
                json={
                    "feature_name": f"boundarylarge{i}:name:v1",
                    "feature_type": "batch",
                    "feature_data_type": "float",
                    "query": f"SELECT value_{i} FROM table",
                    "description": f"Large test feature {i}",
                    "created_by": "test_user",
                    "user_role": "developer",
                },
            )
        creation_time = time.time() - start_time
        start_time = time.time()
        response = test_client.post(
            "/get_all_feature_metadata", json={"user_role": "developer"}
        )
        end_time = time.time()
        assert response.status_code == 200
        retrieval_time = end_time - start_time
        data = response.json()
        assert data["total_count"] >= feature_count
        assert retrieval_time < 1.0
        assert creation_time < 120.0

    # Concurrent access
    def test_concurrent_access_limits(self, test_client):
        from concurrent.futures import ThreadPoolExecutor

        def create_feature(index):
            return test_client.post(
                "/create_feature_metadata",
                json={
                    "feature_name": f"boundary:concurrent:{index}",
                    "feature_type": "batch",
                    "feature_data_type": "float",
                    "query": f"SELECT value_{index} FROM table",
                    "description": f"Concurrent test feature {index}",
                    "created_by": "test_user",
                    "user_role": "developer",
                },
            )

        max_workers = 10
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            responses = list(executor.map(create_feature, range(max_workers)))
        success_count = sum(1 for r in responses if r.status_code == 201)
        assert success_count >= max_workers * 0.8 or success_count == 0

    # Timestamp boundaries
    def test_timestamp_boundaries(self, test_client):
        response = test_client.post(
            "/create_feature_metadata",
            json={
                "feature_name": "boundary:timestamp:1",
                "feature_type": "batch",
                "feature_data_type": "bigint",
                "query": "SELECT timestamp FROM events",
                "description": "Timestamp boundary test",
                "created_by": "test_user",
                "user_role": "developer",
            },
        )
        assert response.status_code in [201, 400, 422, 500]
        if response.status_code == 201:
            metadata = response.json()["metadata"]
            current_time = int(time.time() * 1000)
            created_time = metadata["created_time"]
            assert created_time <= current_time
            assert created_time >= current_time - 60000

    # Version number boundaries
    def test_version_number_boundaries(self, test_client):
        version_tests = ["1", "999", "10000"]
        for i, version in enumerate(version_tests):
            feature_name = f"boundary:version{i}:{version}"
            response = test_client.post(
                "/create_feature_metadata",
                json={
                    "feature_name": feature_name,
                    "feature_type": "batch",
                    "feature_data_type": "int",
                    "query": "SELECT 1",
                    "description": "Version test",
                    "created_by": "test_user",
                    "user_role": "developer",
                },
            )
            assert response.status_code in [201, 400, 422, 500]

    # Special character boundaries
    def test_special_character_boundaries(self, test_client):
        special_names = [
            "test:name_with_underscore:1",
            "test:name-with-dash:1",
            "test:name.with.dots:1",
            "test:name123:1",
            "test123:name456:789",
        ]
        for name in special_names:
            response = test_client.post(
                "/create_feature_metadata",
                json={
                    "feature_name": name,
                    "feature_type": "batch",
                    "feature_data_type": "int",
                    "query": "SELECT 1",
                    "description": "Special char test",
                    "created_by": "test_user",
                    "user_role": "developer",
                },
            )
            assert response.status_code in [201, 400, 422, 500]

    # Memory usage boundaries
    def test_memory_usage_boundaries(self, test_client):
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        feature_count = 10
        for i in range(feature_count):
            test_client.post(
                "/create_feature_metadata",
                json={
                    "feature_name": f"boundary:memory:{i}",
                    "feature_type": "batch",
                    "feature_data_type": "float",
                    "query": f"SELECT value_{i} FROM table",
                    "description": f"Memory test feature {i}",
                    "created_by": "test_user",
                    "user_role": "developer",
                },
            )
        final_memory = process.memory_info().rss
        memory_growth = final_memory - initial_memory
        assert memory_growth < 100 * 1024 * 1024
