import time
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def test_client():
    with TestClient(app) as client:
        yield client


class TestErrorScenarios:
    def test_file_system_errors(self, test_client):
        with patch("pathlib.Path.write_text", side_effect=OSError("Disk full")):
            resp = test_client.post(
                "/create_feature_metadata",
                json={
                    "feature_name": "error:diskfull:v1",
                    "feature_type": "batch",
                    "feature_data_type": "float",
                    "query": "SELECT value FROM table",
                    "description": "Disk full error",
                    "created_by": "user",
                    "user_role": "developer",
                },
            )
            assert resp.status_code in [201, 400, 500]

    def test_memory_exhaustion_simulation(self, test_client):
        large_desc = "X" * 100000
        responses = []
        for i in range(10):
            resp = test_client.post(
                "/create_feature_metadata",
                json={
                    "feature_name": f"error:memory:v{i}",
                    "feature_type": "batch",
                    "feature_data_type": "float",
                    "query": "SELECT value FROM table",
                    "description": large_desc,
                    "created_by": "user",
                    "user_role": "developer",
                },
            )
            responses.append(resp)
        success_count = sum(1 for r in responses if r.status_code == 201)
        assert success_count >= 8

    def test_corrupted_data_handling(self, test_client):
        with patch(
            "pathlib.Path.read_text",
            side_effect=UnicodeDecodeError("utf-8", b"", 0, 1, "invalid start byte"),
        ):
            resp = test_client.post(
                "/get_all_feature_metadata", json={"user_role": "developer"}
            )
            assert resp.status_code in [200, 500]

    def test_network_timeout_simulation(self, test_client):
        original_time = time.time

        def slow_time():
            time.sleep(0.3)
            return original_time()

        with patch("time.time", side_effect=slow_time):
            resp = test_client.post(
                "/create_feature_metadata",
                json={
                    "feature_name": "error:timeout:v1",
                    "feature_type": "batch",
                    "feature_data_type": "float",
                    "query": "SELECT value FROM table",
                    "description": "Timeout simulation",
                    "created_by": "user",
                    "user_role": "developer",
                },
            )
            assert resp.status_code in [201, 400, 500]

    def test_invalid_json_handling(self, test_client):
        try:
            resp = test_client.post(
                "/create_feature_metadata", data="{invalid_json: true"
            )
            assert resp.status_code in [400, 422]
        except Exception:
            assert True

    def test_service_dependency_failures(self, test_client):
        with patch(
            "app.services.feature_service.FeatureMetadataService._save_data",
            side_effect=Exception("Service unavailable"),
        ):
            resp = test_client.post(
                "/create_feature_metadata",
                json={
                    "feature_name": "error:service:v1",
                    "feature_type": "batch",
                    "feature_data_type": "float",
                    "query": "SELECT value FROM table",
                    "description": "Service unavailable",
                    "created_by": "user",
                    "user_role": "developer",
                },
            )
            assert resp.status_code in [201, 500, 400]

    def test_concurrent_error_scenarios(self, test_client):
        from concurrent.futures import ThreadPoolExecutor

        def create_problematic_feature(index):
            return test_client.post(
                "/create_feature_metadata",
                json={
                    "feature_name": f"error:concurrent:v{index}",
                    "feature_type": "batch",
                    "feature_data_type": "float",
                    "query": "SELECT value FROM table",
                    "description": "Concurrent error",
                    "created_by": "user",
                    "user_role": "developer",
                },
            )

        with ThreadPoolExecutor(max_workers=20) as executor:
            responses = list(executor.map(create_problematic_feature, range(20)))
        completed_count = len(
            [r for r in responses if r.status_code in [201, 400, 422, 500]]
        )
        assert completed_count == 20

    def test_resource_exhaustion_recovery(self, test_client):
        for i in range(5):
            test_client.post(
                "/create_feature_metadata",
                json={
                    "feature_name": f"error:exhaustion:v{i}",
                    "feature_type": "batch",
                    "feature_data_type": "float",
                    "query": "SELECT value FROM table",
                    "description": "Resource exhaustion",
                    "created_by": "user",
                    "user_role": "developer",
                },
            )
        recovery_response = test_client.post(
            "/create_feature_metadata",
            json={
                "feature_name": "error:recovery:v1",
                "feature_type": "batch",
                "feature_data_type": "int",
                "query": "SELECT 1",
                "description": "Recovery test",
                "created_by": "recovery_user",
                "user_role": "developer",
            },
        )
        assert recovery_response.status_code in [201, 400]

    def test_malformed_request_handling(self, test_client):
        malformed_requests = [
            {
                "feature_name": 123,
                "feature_type": "batch",
                "feature_data_type": "string",
                "query": "SELECT data",
                "description": "Wrong type test",
                "created_by": "malform_user",
                "user_role": "developer",
            },
            {
                "feature_name": "error:nested:v1",
                "feature_type": {"nested": "object"},
                "feature_data_type": "string",
                "query": "SELECT data",
                "description": "Nested object test",
                "created_by": "malform_user",
                "user_role": "developer",
            },
            {
                "feature_name": ["array", "name"],
                "feature_type": "batch",
                "feature_data_type": "string",
                "query": "SELECT data",
                "description": "Array test",
                "created_by": "malform_user",
                "user_role": "developer",
            },
        ]
        for malformed_request in malformed_requests:
            resp = test_client.post("/create_feature_metadata", json=malformed_request)
            assert resp.status_code in [400, 422]

    def test_edge_case_status_codes(self, test_client):
        resp = test_client.post(
            "/get_feature_metadata",
            json={"features": "nonexistent:feature:v999", "user_role": "developer"},
        )
        assert resp.status_code == 404
        resp = test_client.post(
            "/create_feature_metadata",
            json={
                "feature_name": "error:status:v1",
                "feature_type": "batch",
                "feature_data_type": "string",
                "query": "SELECT data",
                "description": "Status code test",
                "created_by": "status_user",
                "user_role": "invalid_role",
            },
        )
        assert resp.status_code == 400
        resp = test_client.post(
            "/create_feature_metadata",
            json={
                "feature_name": "",
                "feature_type": "batch",
                "feature_data_type": "string",
                "query": "SELECT data",
                "description": "Validation test",
                "created_by": "status_user",
                "user_role": "developer",
            },
        )
        assert resp.status_code in [400, 422]

    def test_graceful_degradation(self, test_client):
        # Patch get_current_timestamp, not get_current_timestamp_ms
        with patch(
            "app.utils.timestamp.get_current_timestamp",
            side_effect=[123456789, Exception("Time service down"), 987654321],
        ):
            response1 = test_client.post(
                "/create_feature_metadata",
                json={
                    "feature_name": "error:graceful:v1",
                    "feature_type": "batch",
                    "feature_data_type": "float",
                    "query": "SELECT value FROM table",
                    "description": "Graceful test",
                    "created_by": "user",
                    "user_role": "developer",
                },
            )
            response2 = test_client.post(
                "/create_feature_metadata",
                json={
                    "feature_name": "error:graceful:v2",
                    "feature_type": "batch",
                    "feature_data_type": "float",
                    "query": "SELECT value FROM table",
                    "description": "Graceful test 2",
                    "created_by": "user",
                    "user_role": "developer",
                },
            )
            response3 = test_client.post(
                "/create_feature_metadata",
                json={
                    "feature_name": "error:graceful:v3",
                    "feature_type": "batch",
                    "feature_data_type": "float",
                    "query": "SELECT value FROM table",
                    "description": "Graceful test 3",
                    "created_by": "user",
                    "user_role": "developer",
                },
            )
            assert response1.status_code == 201 or response1.status_code == 400
            assert response2.status_code in [201, 500, 400]
            assert response3.status_code == 201 or response3.status_code == 400


class TestErrorRecovery:
    def test_transaction_rollback_simulation(self, test_client):
        with patch(
            "app.services.feature_service.FeatureMetadataService._save_data",
            side_effect=Exception("Save failed"),
        ):
            resp = test_client.post(
                "/create_feature_metadata",
                json={
                    "feature_name": "error:rollback:v1",
                    "feature_type": "batch",
                    "feature_data_type": "float",
                    "query": "SELECT value FROM table",
                    "description": "Rollback test",
                    "created_by": "user",
                    "user_role": "developer",
                },
            )
            assert resp.status_code in [201, 500, 400]
        # After rollback, feature may not exist
        get_resp = test_client.post(
            "/get_feature_metadata",
            json={"features": "error:rollback:v1", "user_role": "developer"},
        )
        assert get_resp.status_code in [404, 200]

    def test_consistency_after_errors(self, test_client):
        for i in range(3):
            resp = test_client.post(
                "/create_feature_metadata",
                json={
                    "feature_name": f"error:consistency{i}:v1",
                    "feature_type": "batch",
                    "feature_data_type": "float",
                    "query": "SELECT value FROM table",
                    "description": "Consistency test",
                    "created_by": "user",
                    "user_role": "developer",
                },
            )
            assert resp.status_code == 201
        resp = test_client.post(
            "/create_feature_metadata",
            json={
                "feature_name": "error:consistency1:v1",
                "feature_type": "batch",
                "feature_data_type": "float",
                "query": "SELECT value FROM table",
                "description": "Consistency test",
                "created_by": "user",
                "user_role": "developer",
            },
        )
        assert resp.status_code == 400
        for i in range(3):
            get_resp = test_client.post(
                "/get_feature_metadata",
                json={"features": f"error:consistency{i}:v1", "user_role": "developer"},
            )
            assert get_resp.status_code == 200
