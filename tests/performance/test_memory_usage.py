import gc
import os

import psutil
import pytest
from fastapi.testclient import TestClient

from app.main import app


class TestMemoryUsage:
    """Test memory usage patterns."""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = TestClient(app)
        self.process = psutil.Process(os.getpid())
        gc.collect()
        self.baseline_memory = self.process.memory_info().rss / (1024 * 1024)

    def get_current_memory(self):
        gc.collect()
        return self.process.memory_info().rss / (1024 * 1024)

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
