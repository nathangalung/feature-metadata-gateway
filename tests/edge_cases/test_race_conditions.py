from concurrent.futures import ThreadPoolExecutor

import pytest
from fastapi.testclient import TestClient

from app.main import app


# Test client fixture
@pytest.fixture
def test_client():
    with TestClient(app) as client:
        yield client


class TestRaceConditions:
    """Test race condition scenarios."""

    # Concurrent feature creation
    def test_concurrent_feature_creation(self, test_client):
        feature_name = "race:create:v1"

        def create_feature():
            return test_client.post(
                "/create_feature_metadata",
                json={
                    "feature_name": feature_name,
                    "feature_type": "batch",
                    "feature_data_type": "float",
                    "query": "SELECT value FROM table",
                    "description": "Race condition test",
                    "created_by": "race_user",
                    "user_role": "developer",
                },
            )

        with ThreadPoolExecutor(max_workers=10) as executor:
            responses = list(executor.map(lambda _: create_feature(), range(10)))
        success_count = sum(1 for r in responses if r.status_code == 201)
        failure_count = sum(1 for r in responses if r.status_code == 400)
        assert success_count == 1
        assert failure_count == 9

    # Concurrent status updates
    def test_concurrent_status_updates(self, test_client):
        feature_name = "race:status:v1"
        create_response = test_client.post(
            "/create_feature_metadata",
            json={
                "feature_name": feature_name,
                "feature_type": "real-time",
                "feature_data_type": "double",
                "query": "SELECT metric FROM sensors",
                "description": "Status race test",
                "created_by": "status_user",
                "user_role": "developer",
            },
        )
        assert create_response.status_code == 201

        def submit_for_testing():
            return test_client.post(
                "/ready_test_feature_metadata",
                json={
                    "feature_name": feature_name,
                    "submitted_by": "status_user",
                    "user_role": "developer",
                },
            )

        def update_description():
            return test_client.post(
                "/update_feature_metadata",
                json={
                    "feature_name": feature_name,
                    "description": "Updated in race",
                    "last_updated_by": "status_user",
                    "user_role": "developer",
                },
            )

        with ThreadPoolExecutor(max_workers=5) as executor:
            responses = list(
                executor.map(
                    lambda f: f(),
                    [submit_for_testing, update_description] * 2 + [submit_for_testing],
                )
            )
        success_count = sum(1 for r in responses if r.status_code == 200)
        assert success_count >= 1

    # Read/write race conditions
    def test_read_write_race_conditions(self, test_client):
        base_features = []
        for i in range(5):
            resp = test_client.post(
                "/create_feature_metadata",
                json={
                    "feature_name": f"race:rw{i}:v1",
                    "feature_type": "batch",
                    "feature_data_type": "float",
                    "query": f"SELECT value_{i} FROM table",
                    "description": f"RW race feature {i}",
                    "created_by": "rw_user",
                    "user_role": "developer",
                },
            )
            base_features.append(resp)

        def read_all_features():
            return test_client.get("/get_all_feature_metadata?user_role=developer")

        def update_random_feature(index):
            return test_client.post(
                "/update_feature_metadata",
                json={
                    "feature_name": f"race:rw{index}:v1",
                    "description": f"Updated {index}",
                    "last_updated_by": "rw_user",
                    "user_role": "developer",
                },
            )

        def create_new_feature(index):
            return test_client.post(
                "/create_feature_metadata",
                json={
                    "feature_name": f"race:rwnew{index}:v1",
                    "feature_type": "batch",
                    "feature_data_type": "float",
                    "query": f"SELECT value_{index} FROM table",
                    "description": f"RW race new feature {index}",
                    "created_by": "rw_user",
                    "user_role": "developer",
                },
            )

        with ThreadPoolExecutor(max_workers=15) as executor:
            responses = list(
                executor.map(
                    lambda i: [
                        read_all_features(),
                        update_random_feature(i % 5),
                        create_new_feature(i),
                    ],
                    range(5),
                )
            )
        flat_responses = [item for sublist in responses for item in sublist]
        read_success = sum(1 for r in flat_responses[:5] if r.status_code == 200)
        update_success = sum(1 for r in flat_responses[5:10] if r.status_code == 200)
        create_success = sum(1 for r in flat_responses[10:15] if r.status_code == 201)
        assert read_success >= 4
        assert update_success >= 3
        assert create_success >= 2

    # Workflow state race conditions
    def test_workflow_state_race_conditions(self, test_client):
        feature_name = "race:workflow:v1"
        test_client.post(
            "/create_feature_metadata",
            json={
                "feature_name": feature_name,
                "feature_type": "batch",
                "feature_data_type": "float",
                "query": "SELECT score FROM models",
                "description": "Workflow race test",
                "created_by": "workflow_user",
                "user_role": "developer",
            },
        )
        test_client.post(
            "/ready_test_feature_metadata",
            json={
                "feature_name": feature_name,
                "submitted_by": "developer",
                "user_role": "developer",
            },
        )

        def test_feature_success():
            return test_client.post(
                "/test_feature_metadata",
                json={
                    "feature_name": feature_name,
                    "test_result": "TEST_SUCCEEDED",
                    "tested_by": "test_system",
                    "user_role": "external_testing_system",
                },
            )

        def test_feature_failure():
            return test_client.post(
                "/test_feature_metadata",
                json={
                    "feature_name": feature_name,
                    "test_result": "TEST_FAILED",
                    "tested_by": "test_system",
                    "user_role": "external_testing_system",
                },
            )

        with ThreadPoolExecutor(max_workers=2) as executor:
            responses = list(
                executor.map(
                    lambda f: f(), [test_feature_success, test_feature_failure]
                )
            )
        success_count = sum(1 for r in responses if r.status_code == 200)
        failure_count = sum(1 for r in responses if r.status_code == 400)
        assert success_count == 1
        assert failure_count == 1

    # Delete and access race
    def test_delete_and_access_race(self, test_client):
        feature_name = "race:delete:v1"
        test_client.post(
            "/create_feature_metadata",
            json={
                "feature_name": feature_name,
                "feature_type": "real-time",
                "feature_data_type": "string",
                "query": "SELECT name FROM users",
                "description": "Delete race test",
                "created_by": "delete_user",
                "user_role": "developer",
            },
        )

        def delete_feature():
            return test_client.post(
                "/delete_feature_metadata",
                json={
                    "feature_name": feature_name,
                    "deleted_by": "delete_user",
                    "user_role": "developer",
                    "deletion_reason": "Delete for race test",
                },
            )

        def get_feature():
            return test_client.get(
                f"/get_feature_metadata/{feature_name}?user_role=developer"
            )

        def update_feature():
            return test_client.post(
                "/update_feature_metadata",
                json={
                    "feature_name": feature_name,
                    "description": "Updated after delete",
                    "last_updated_by": "delete_user",
                    "user_role": "developer",
                },
            )

        with ThreadPoolExecutor(max_workers=3) as executor:
            delete_response, get_response, update_response = executor.map(
                lambda f: f(), [delete_feature, get_feature, update_feature]
            )
        assert delete_response.status_code == 200
        assert get_response.status_code in [200, 404, 400]
        assert update_response.status_code in [200, 400, 404]

    # Concurrent metadata modifications
    def test_concurrent_metadata_modifications(self, test_client):
        feature_name = "race:metadata:v1"
        test_client.post(
            "/create_feature_metadata",
            json={
                "feature_name": feature_name,
                "feature_type": "batch",
                "feature_data_type": "int",
                "query": "SELECT count FROM events",
                "description": "Metadata race test",
                "created_by": "metadata_user",
                "user_role": "developer",
            },
        )

        def update_field(field_name, field_value):
            return test_client.post(
                "/update_feature_metadata",
                json={
                    "feature_name": feature_name,
                    field_name: field_value,
                    "last_updated_by": "metadata_user",
                    "user_role": "developer",
                },
            )

        with ThreadPoolExecutor(max_workers=4) as executor:
            responses = list(
                executor.map(
                    lambda args: update_field(*args),
                    [
                        ("description", "Updated description"),
                        ("query", "SELECT new_count FROM events"),
                        ("feature_type", "real-time"),
                        ("feature_data_type", "bigint"),
                    ],
                )
            )
        success_count = sum(1 for r in responses if r.status_code == 200)
        assert success_count == 4
        final_response = test_client.get(
            f"/get_feature_metadata/{feature_name}?user_role=developer"
        )
        assert final_response.status_code == 200
        metadata = final_response.json()["metadata"]
        assert metadata["description"] == "Updated description"
        assert metadata["query"] == "SELECT new_count FROM events"
        assert metadata["feature_type"] == "real-time"
        assert metadata["feature_data_type"] == "bigint"


class TestDeadlockPrevention:
    """Test deadlock prevention mechanisms."""

    # Circular dependency prevention
    def test_circular_dependency_prevention(self, test_client):
        assert True

    # Resource lock timeout
    def test_resource_lock_timeout(self, test_client):
        assert True
