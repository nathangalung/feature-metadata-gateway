import gc
import os

import psutil
import pytest
from fastapi.testclient import TestClient

from app.main import app


class TestMemoryUsage:
    """Test memory usage patterns."""

    # Setup test client and memory
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = TestClient(app)
        self.process = psutil.Process(os.getpid())
        gc.collect()
        self.baseline_memory = self.process.memory_info().rss / (1024 * 1024)

    # Get current memory usage
    def get_current_memory(self):
        gc.collect()
        return self.process.memory_info().rss / (1024 * 1024)

    # Large entity batch memory
    def test_memory_usage_for_large_entity_batch(self):
        pytest.importorskip("psutil")
        entity_count = 1000
        entities = {"entity_id": [f"entity_{i}" for i in range(entity_count)]}
        payload = {
            "features": [
                "driver_hourly_stats:conv_rate:1",
                "driver_hourly_stats:acc_rate:2",
            ],
            "entities": entities,
        }
        before = self.get_current_memory()
        response = self.client.post("/features", json=payload)
        assert response.status_code == 200
        after = self.get_current_memory()
        increase = after - before
        print(f"Baseline: {self.baseline_memory:.2f} MB")
        print(f"Before: {before:.2f} MB")
        print(f"After: {after:.2f} MB")
        print(f"Increase: {increase:.2f} MB")
        assert increase < 100

    # Memory growth repeated requests
    def test_memory_growth_during_repeated_requests(self):
        pytest.importorskip("psutil")
        payload = {
            "features": ["driver_hourly_stats:conv_rate:1"],
            "entities": {"entity_id": ["test_entity"]},
        }
        before = self.get_current_memory()
        for _ in range(100):
            response = self.client.post("/features", json=payload)
            assert response.status_code == 200
        after = self.get_current_memory()
        total_growth = after - before
        per_request = total_growth / 100 if 100 > 0 else 0
        print(f"Before: {before:.2f} MB")
        print(f"After: {after:.2f} MB")
        print(f"Total growth: {total_growth:.2f} MB")
        print(f"Per request: {per_request:.4f} MB")
        assert per_request < 0.1

    # Metadata operations memory stability
    def test_metadata_operations_memory_stability(self):
        pytest.importorskip("psutil")
        before = self.get_current_memory()
        for i in range(10):
            self.client.post(
                "/create_feature_metadata",
                json={
                    "feature_name": f"memory:test:v{i}",
                    "feature_type": "batch",
                    "feature_data_type": "float",
                    "query": f"SELECT value_{i} FROM table",
                    "description": f"Memory test feature {i}",
                    "created_by": "test_user",
                    "user_role": "developer",
                },
            )
            self.client.post(
                "/get_all_feature_metadata", json={"user_role": "developer"}
            )
        after = self.get_current_memory()
        total_growth = after - before
        print(f"Before ops: {before:.2f} MB")
        print(f"After ops: {after:.2f} MB")
        print(f"Total growth: {total_growth:.2f} MB")
        assert total_growth < 10
