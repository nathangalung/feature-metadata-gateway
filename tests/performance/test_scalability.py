import time

import pytest
from fastapi.testclient import TestClient

from app.main import app


class TestScalability:
    """Test scalability of the service."""

    @pytest.fixture(autouse=True)
    def setup(self):
        with TestClient(app) as client:
            self.client = client
            yield

    # Metadata scaling with count
    def test_metadata_scaling_with_feature_count(self):
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
            resp = self.client.post(
                "/get_all_feature_metadata", json={"user_role": "developer"}
            )
            end = time.time()
            assert resp.status_code == 200
            get_all_times.append(end - start)
            print(f"Get all {count}: {end - start:.4f} seconds")
        if len(get_all_times) > 1 and get_all_times[0] > 0:
            scaling = get_all_times[-1] / get_all_times[0]
            print(f"Get all scaling: {scaling:.2f}x")
            assert scaling < 10
