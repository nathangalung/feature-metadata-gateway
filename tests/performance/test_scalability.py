"""Performance tests for scalability."""

import time

import pytest
from fastapi.testclient import TestClient

from app.main import app


class TestScalability:
    """Test scalability of the service."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test client."""
        with TestClient(app) as client:
            self.client = client
            yield

    def test_batch_size_scaling(self):
        """Test scaling with batch size."""
        batch_sizes = [1, 10, 100, 500]
        response_times = []
        for size in batch_sizes:
            entities = {"entity_id": [f"entity_{i}" for i in range(size)]}
            payload = {
                "features": [
                    "driver_hourly_stats:conv_rate:1",
                    "driver_hourly_stats:acc_rate:2",
                ],
                "entities": entities,
            }
            start = time.time()
            resp = self.client.post("/features", json=payload)
            end = time.time()
            assert resp.status_code == 200 or resp.status_code == 404
            response_times.append(end - start)
            print(f"Batch size {size}: {end - start:.4f} seconds")
        for i, size in enumerate(batch_sizes):
            print(f"Batch size {size}: {response_times[i]:.4f} seconds")
        if response_times[0] > 0:
            scaling = response_times[-1] / response_times[0]
            print(f"Scaling factor: {scaling:.2f}x")
            assert scaling < len(batch_sizes)

    def test_feature_count_scaling(self):
        """Test scaling with feature count."""
        feature_counts = [1, 2, 3, 4, 5]
        response_times = []
        base_features = [
            "driver_hourly_stats:conv_rate:1",
            "driver_hourly_stats:acc_rate:2",
            "driver_hourly_stats:avg_daily_trips:3",
            "fraud:amount:v1",
            "customer:income:v1",
        ]
        for count in feature_counts:
            features = base_features[:count]
            payload = {
                "features": features,
                "entities": {"entity_id": ["test_entity_1", "test_entity_2"]},
            }
            start = time.time()
            resp = self.client.post("/features", json=payload)
            end = time.time()
            assert resp.status_code == 200 or resp.status_code == 404
            response_times.append(end - start)
            print(f"Feature count {count}: {end - start:.4f} seconds")
        if len(response_times) > 1 and response_times[0] > 0:
            scaling = response_times[-1] / response_times[0]
            print(f"Feature count scaling: {scaling:.2f}x")
            assert scaling < 2 * feature_counts[-1]

    def test_metadata_scaling_with_feature_count(self):
        """Test metadata scaling with count."""
        feature_counts = [10, 20, 50, 100]
        get_all_times = []
        for count in feature_counts:
            for i in range(count):
                self.client.post(
                    "/create_feature_metadata",
                    json={
                        "feature_name": f"scaling:test:v{i}",
                        "feature_type": "batch",
                        "feature_data_type": "float",
                        "query": f"SELECT value_{i} FROM table",
                        "description": f"Scaling test feature {i}",
                        "created_by": "test_user",
                        "user_role": "developer",
                    },
                )
            start = time.time()
            resp = self.client.get("/get_all_feature_metadata?user_role=developer")
            end = time.time()
            assert resp.status_code == 200
            get_all_times.append(end - start)
            print(f"Get all {count}: {end - start:.4f} seconds")
            # In real test, would reset data here
        if len(get_all_times) > 1 and get_all_times[0] > 0:
            scaling = get_all_times[-1] / get_all_times[0]
            print(f"Get all scaling: {scaling:.2f}x")
            assert scaling < 10
