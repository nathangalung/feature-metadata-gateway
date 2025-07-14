import pytest
from fastapi.testclient import TestClient

from app.main import app


# Test client fixture
@pytest.fixture
def test_client():
    with TestClient(app) as client:
        yield client


class TestDataValidation:
    """Test data validation edge cases."""

    # Test null/empty values
    def test_null_and_empty_values(self, test_client):
        test_cases = [
            {"feature_name": "", "should_fail": True, "field": "feature_name"},
            {"created_by": "", "should_fail": True, "field": "created_by"},
            {"description": "", "should_fail": False, "field": "description"},
            {
                "feature_name": "a:b:v1",
                "created_by": "u",
                "description": "x",
                "should_fail": False,
                "field": "valid_short",
            },
        ]
        base_payload = {
            "feature_name": "edge:null:v1",
            "feature_type": "batch",
            "feature_data_type": "int",
            "query": "SELECT 1",
            "description": "Test feature",
            "created_by": "edge_user",
            "user_role": "developer",
        }
        for i, test_case in enumerate(test_cases):
            payload = base_payload.copy()
            for key, value in test_case.items():
                if key not in ["should_fail", "field"]:
                    payload[key] = value
            if "feature_name" in payload and payload["feature_name"]:
                payload["feature_name"] = f"edge:null{i}:v1"
            response = test_client.post("/create_feature_metadata", json=payload)
            if test_case.get("should_fail"):
                assert response.status_code in [
                    400,
                    422,
                ], f"Expected failure for {test_case['field']}"
            else:
                assert response.status_code in [
                    201,
                    422,
                ], f"Expected success for {test_case['field']}"

    # Test invalid enum values
    def test_invalid_enum_values(self, test_client):
        invalid_types = [
            "BATCH",
            "streaming",
            "real_time",
            "compute_first",
            "",
            None,
            123,
            "batch_processing",
        ]
        for i, invalid_type in enumerate(invalid_types):
            response = test_client.post(
                "/create_feature_metadata",
                json={
                    "feature_name": f"edge:invalidtype{i}:v1",
                    "feature_type": invalid_type,
                    "feature_data_type": "string",
                    "query": "SELECT data FROM table",
                    "description": "Invalid type test",
                    "created_by": "edge_user",
                    "user_role": "developer",
                },
            )
            assert response.status_code in [400, 422]
        invalid_data_types = [
            "STRING",
            "varchar",
            "text",
            "number",
            "",
            "int32",
        ]
        for i, invalid_data_type in enumerate(invalid_data_types):
            response = test_client.post(
                "/create_feature_metadata",
                json={
                    "feature_name": f"edge:invaliddatatype{i}:v1",
                    "feature_type": "batch",
                    "feature_data_type": invalid_data_type,
                    "query": "SELECT data FROM table",
                    "description": "Invalid data type test",
                    "created_by": "edge_user",
                    "user_role": "developer",
                },
            )
            assert response.status_code in [400, 422]

    # Test invalid feature name formats
    def test_invalid_feature_name_formats(self, test_client):
        invalid_names = [
            "invalid_format",
            "only:one:colon",
            ":missing:category",
            "category::v1",
            "category:name:",
            "category:name:v1:extra",
            "cat name:test:v1",
            "cat:na me:v1",
            "cat:name:v 1",
            "",
            "::::",
            "a:b",
            "a:::",
        ]
        for i, invalid_name in enumerate(invalid_names):
            response = test_client.post(
                "/create_feature_metadata",
                json={
                    "feature_name": invalid_name,
                    "feature_type": "batch",
                    "feature_data_type": "string",
                    "query": "SELECT data FROM table",
                    "description": f"Invalid name test {i}",
                    "created_by": "edge_user",
                    "user_role": "developer",
                },
            )
            assert response.status_code in [
                400,
                422,
            ], f"Should reject invalid name: {invalid_name}"

    # Test SQL query validation
    def test_sql_query_validation(self, test_client):
        query_tests = [
            ("SELECT * FROM table", True),
            ("SELECT col1, col2 FROM table WHERE condition = 1", True),
            ("SELECT COUNT(*) FROM users", True),
            ("", False),
            ("   ", False),
            ("NOT A VALID SQL", True),
            ("SELECT 'string with; semicolon'", True),
        ]
        for i, (query, should_succeed) in enumerate(query_tests):
            response = test_client.post(
                "/create_feature_metadata",
                json={
                    "feature_name": f"edge:query{i}:v1",
                    "feature_type": "batch",
                    "feature_data_type": "string",
                    "query": query,
                    "description": "Query validation test",
                    "created_by": "edge_user",
                    "user_role": "developer",
                },
            )
            if should_succeed:
                assert response.status_code == 201, f"Query should be accepted: {query}"
            else:
                assert response.status_code in [
                    400,
                    422,
                ], f"Query should be rejected: {query}"

    # Test JSON structure validation
    def test_json_structure_validation(self, test_client):
        incomplete_payloads = [
            {"feature_name": "test:incomplete:v1"},
            {"feature_name": "test:incomplete:v2", "feature_type": "batch"},
            {},
        ]
        for i, payload in enumerate(incomplete_payloads):
            response = test_client.post("/create_feature_metadata", json=payload)
            assert response.status_code in [
                400,
                422,
            ], f"Should reject incomplete payload {i}"

    # Test circular reference prevention
    def test_circular_reference_prevention(self, test_client):
        test_cases = [
            {
                "feature_name": "circular:ref:v1",
                "query": "SELECT feature_value FROM circular:ref:v1",
                "description": "Circular reference test",
            },
            {
                "feature_name": "circular:mutual:v1",
                "query": "SELECT value FROM circular:mutual:v2",
                "description": "Mutual reference test",
            },
        ]
        for _i, test_case in enumerate(test_cases):
            payload = {
                "feature_type": "batch",
                "feature_data_type": "float",
                "created_by": "circular_user",
                "user_role": "developer",
                **test_case,
            }
            response = test_client.post("/create_feature_metadata", json=payload)
            assert response.status_code in [201, 400, 422]

    # Test data type consistency
    def test_data_type_consistency(self, test_client):
        mismatch_tests = [
            {
                "feature_data_type": "int",
                "query": "SELECT 'string_value'",
                "should_warn": False,
            },
            {
                "feature_data_type": "string",
                "query": "SELECT 123.45",
                "should_warn": False,
            },
            {
                "feature_data_type": "boolean",
                "query": "SELECT COUNT(*)",
                "should_warn": False,
            },
        ]
        for i, test in enumerate(mismatch_tests):
            response = test_client.post(
                "/create_feature_metadata",
                json={
                    "feature_name": f"edge:mismatch{i}:v1",
                    "feature_type": "batch",
                    "feature_data_type": test["feature_data_type"],
                    "query": test["query"],
                    "description": "Data type mismatch test",
                    "created_by": "mismatch_user",
                    "user_role": "developer",
                },
            )
            assert response.status_code == 201

    # Test concurrent validation
    def test_concurrent_validation_edge_cases(self, test_client):
        from concurrent.futures import ThreadPoolExecutor

        def create_similar_feature(index):
            return test_client.post(
                "/create_feature_metadata",
                json={
                    "feature_name": f"concurrent:validation{index}:v1",
                    "feature_type": "batch",
                    "feature_data_type": "string",
                    "query": f"SELECT data_{index} FROM table",
                    "description": f"Concurrent validation test {index}",
                    "created_by": f"user_{index}",
                    "user_role": "developer",
                },
            )

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(create_similar_feature, i) for i in range(10)]
            responses = [future.result() for future in futures]
        success_count = sum(1 for r in responses if r.status_code == 201)
        assert success_count == 10, "All features with unique names should be created"

        def create_duplicate_feature():
            return test_client.post(
                "/create_feature_metadata",
                json={
                    "feature_name": "concurrent:duplicate:v1",
                    "feature_type": "real-time",
                    "feature_data_type": "float",
                    "query": "SELECT duplicate FROM table",
                    "description": "Duplicate test",
                    "created_by": "duplicate_user",
                    "user_role": "developer",
                },
            )

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(create_duplicate_feature) for _ in range(5)]
            responses = [future.result() for future in futures]
        success_count = sum(1 for r in responses if r.status_code == 201)
        failure_count = sum(1 for r in responses if r.status_code == 400)
        assert success_count == 1, "Only one duplicate feature should be created"
        assert failure_count == 4, "Four attempts should fail due to duplicate"
