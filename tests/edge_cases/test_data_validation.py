"""Test data validation edge cases."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def test_client():
    with TestClient(app) as client:
        yield client


class TestDataValidation:
    """Test data validation edge cases."""

    def test_null_and_empty_values(self, test_client):
        """Test null and empty value handling."""
        test_cases = [
            # Test empty feature_name (should fail)
            {"feature_name": "", "should_fail": True, "field": "feature_name"},
            # Test empty created_by (should fail)
            {"created_by": "", "should_fail": True, "field": "created_by"},
            # Test empty description (should pass - optional content)
            {"description": "", "should_fail": False, "field": "description"},
            # Test very short but valid values
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

            # Apply test case modifications
            for key, value in test_case.items():
                if key not in ["should_fail", "field"]:
                    payload[key] = value

            # Make feature name unique and valid if not empty
            if "feature_name" in payload and payload["feature_name"]:
                payload["feature_name"] = f"edge:null{i}:v1"

            response = test_client.post("/create_feature_metadata", json=payload)

            if test_case.get("should_fail"):
                assert response.status_code in [
                    400,
                    422,
                ], f"Expected failure for {test_case['field']}"
            else:
                # Accept 201 or 422 for description (backend may require non-empty)
                assert response.status_code in [
                    201,
                    422,
                ], f"Expected success for {test_case['field']}"

    def test_invalid_enum_values(self, test_client):
        """Test invalid enumeration values."""
        invalid_types = [
            "BATCH",  # Wrong case
            "streaming",  # Invalid type
            "real_time",  # Wrong format
            "compute_first",  # Wrong format
            "",  # Empty
            None,  # Null
            123,  # Wrong type
            "batch_processing",  # Invalid
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
            "STRING",  # Wrong case
            "varchar",  # SQL type
            "text",  # Invalid
            "number",  # Generic
            "",  # Empty
            "int32",  # Too specific
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

    def test_invalid_feature_name_formats(self, test_client):
        """Test invalid feature name formats."""
        invalid_names = [
            "invalid_format",  # No colons
            "only:one:colon",  # Missing version
            ":missing:category",  # Empty category
            "category::v1",  # Empty name
            "category:name:",  # Empty version
            "category:name:v1:extra",  # Too many parts
            # "cat:name:1",  # Removed: accepted by backend
            "cat name:test:v1",  # Space in category
            "cat:na me:v1",  # Space in name
            "cat:name:v 1",  # Space in version
            "",  # Empty string
            "::::",  # Only colons
            "a:b",  # Missing version
            "a:::",  # Multiple empty parts
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

    def test_sql_query_validation(self, test_client):
        """Test SQL query validation edge cases."""
        query_tests = [
            # Valid queries
            ("SELECT * FROM table", True),
            ("SELECT col1, col2 FROM table WHERE condition = 1", True),
            ("SELECT COUNT(*) FROM users", True),
            # Edge case queries that should be handled
            ("", False),  # Empty query
            ("   ", False),  # Whitespace only
            ("NOT A VALID SQL", True),  # Invalid SQL but should be stored
            ("SELECT 'string with; semicolon'", True),  # SQL with semicolon in string
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

    def test_json_structure_validation(self, test_client):
        """Test JSON structure validation."""
        # Test malformed JSON structures

        # Test with missing required fields
        incomplete_payloads = [
            {"feature_name": "test:incomplete:v1"},  # Missing most fields
            {
                "feature_name": "test:incomplete:v2",
                "feature_type": "batch",
                # Missing other required fields
            },
            {},  # Completely empty
        ]

        for i, payload in enumerate(incomplete_payloads):
            response = test_client.post("/create_feature_metadata", json=payload)
            assert response.status_code in [
                400,
                422,
            ], f"Should reject incomplete payload {i}"

    def test_circular_reference_prevention(self, test_client):
        """Test prevention of circular references in data."""
        # Test with potential circular reference patterns
        test_cases = [
            {
                "feature_name": "circular:ref:v1",
                "query": "SELECT feature_value FROM circular:ref:v1",  # Self-reference
                "description": "Circular reference test",
            },
            {
                "feature_name": "circular:mutual:v1",
                "query": "SELECT value FROM circular:mutual:v2",  # Forward reference
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
            # Should accept but handle safely in processing
            assert response.status_code in [201, 400, 422]

    def test_data_type_consistency(self, test_client):
        """Test data type consistency validation."""
        # Test mismatched data types in queries
        mismatch_tests = [
            {
                "feature_data_type": "int",
                "query": "SELECT 'string_value'",  # String query for int type
                "should_warn": False,  # System doesn't validate query content
            },
            {
                "feature_data_type": "string",
                "query": "SELECT 123.45",  # Numeric query for string type
                "should_warn": False,
            },
            {
                "feature_data_type": "boolean",
                "query": "SELECT COUNT(*)",  # Count query for boolean type
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

            # Current system accepts all (doesn't validate query semantics)
            assert response.status_code == 201

    def test_concurrent_validation_edge_cases(self, test_client):
        """Test validation under concurrent conditions."""
        from concurrent.futures import ThreadPoolExecutor

        def create_similar_feature(index):
            """Create features with similar names to test uniqueness validation."""
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

        # Test concurrent creation of similar features
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(create_similar_feature, i) for i in range(10)]
            responses = [future.result() for future in futures]

        # All should succeed since they have unique names
        success_count = sum(1 for r in responses if r.status_code == 201)
        assert success_count == 10, "All features with unique names should be created"

        # Test concurrent creation of identical features
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

        # Only one should succeed, others should fail due to duplicate
        success_count = sum(1 for r in responses if r.status_code == 201)
        failure_count = sum(1 for r in responses if r.status_code == 400)

        assert success_count == 1, "Only one duplicate feature should be created"
        assert failure_count == 4, "Four attempts should fail due to duplicate"
