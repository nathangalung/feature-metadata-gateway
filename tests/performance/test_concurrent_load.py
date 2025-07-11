# """Performance tests for concurrent load handling."""

# import time
# from concurrent.futures import ThreadPoolExecutor

# import pytest
# from fastapi.testclient import TestClient

# from app.main import app


# class TestConcurrentLoad:
#     """Test concurrent load handling."""

#     @pytest.fixture(autouse=True)
#     def setup(self):
#         """Setup test client."""
#         self.client = TestClient(app)

#     def test_concurrent_feature_requests(self):
#         """Test concurrent feature requests."""
#         entities = {"entity_id": [f"entity_{i}" for i in range(10)]}
#         payload = {
#             "features": [
#                 "driver_hourly_stats:conv_rate:1",
#                 "driver_hourly_stats:acc_rate:2"
#             ],
#             "entities": entities
#         }
#         def make_request():
#             return self.client.post("/features", json=payload)
#         start_time = time.time()
#         with ThreadPoolExecutor(max_workers=10) as executor:
#             futures = [executor.submit(make_request) for _ in range(10)]
#             responses = [f.result() for f in futures]
#         end_time = time.time()
#         assert all(r.status_code == 200 for r in responses)
#         total_time = end_time - start_time
#         throughput = len(responses) / total_time
#         print(f"Concurrent requests: {len(responses)}")
#         print(f"Total time: {total_time:.4f} seconds")
#         print(f"Throughput: {throughput:.2f} req/s")
#         assert throughput > 1.0

#     def test_concurrent_metadata_operations(self):
#         """Test concurrent metadata operations."""
#         def create_feature(idx):
#             return self.client.post("/create_feature_metadata", json={
#                 "feature_name": f"concurrent:load:v{idx}",
#                 "feature_type": "batch",
#                 "feature_data_type": "float",
#                 "query": f"SELECT value_{idx} FROM table",
#                 "description": f"Concurrent test feature {idx}",
#                 "created_by": "test_user",
#                 "user_role": "developer"
#             })
#         def get_all_features():
#             return self.client.post("/get_all_feature_metadata", json={
#                 "user_role": "developer"
#             })
#         with ThreadPoolExecutor(max_workers=20) as executor:
#             create_futures = [executor.submit(create_feature, i) for i in range(10)]
#             read_futures = [executor.submit(get_all_features) for _ in range(10)]
#             create_responses = [f.result() for f in create_futures]
#             read_responses = [f.result() for f in read_futures]
#         assert sum(1 for r in create_responses if r.status_code == 201) > 0
#         assert sum(1 for r in read_responses if r.status_code == 200) > 0

#     def test_health_check_under_load(self):
#         """Test health check under load."""
#         def feature_request():
#             return self.client.post("/features", json={
#                 "features": ["driver_hourly_stats:conv_rate:1"],
#                 "entities": {"entity_id": ["test_entity"]}
#             })
#         def health_check():
#             return self.client.post("/health")
#         with ThreadPoolExecutor(max_workers=20) as executor:
#             load_futures = [executor.submit(feature_request) for _ in range(10)]
#             health_futures = [executor.submit(health_check) for _ in range(5)]
#             health_responses = [f.result() for f in health_futures]
#         for resp in health_responses:
#             assert resp.status_code == 200
#             data = resp.json()
#             assert data["status"] == "healthy"
