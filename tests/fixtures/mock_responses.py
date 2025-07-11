"""Mock response data for testing."""

from typing import Any

from app.utils.timestamp import get_current_timestamp_ms


class MockResponses:
    """Mock response data for API."""

    @staticmethod
    def get_successful_create_response(feature_name: str = "test:feature:v1") -> dict[str, Any]:
        ts = get_current_timestamp_ms()
        return {
            "success": True,
            "message": "Feature created successfully",
            "metadata": {
                "feature_name": feature_name,
                "feature_type": "batch",
                "feature_data_type": "float",
                "query": "SELECT value FROM test_table",
                "description": "Test feature",
                "status": "DRAFT",
                "created_time": ts,
                "updated_time": ts,
                "created_by": "test_developer",
                "last_updated_by": "test_developer"
            },
            "event_timestamp": ts
        }

    @staticmethod
    def get_successful_update_response(feature_name: str = "test:feature:v1") -> dict[str, Any]:
        ts = get_current_timestamp_ms()
        return {
            "success": True,
            "message": "Feature updated successfully",
            "metadata": {
                "feature_name": feature_name,
                "feature_type": "batch",
                "feature_data_type": "float",
                "query": "SELECT value FROM test_table",
                "description": "Updated test feature description",
                "status": "DRAFT",
                "created_time": ts - 3600000,
                "updated_time": ts,
                "created_by": "test_developer",
                "last_updated_by": "test_updater"
            },
            "event_timestamp": ts
        }

    @staticmethod
    def get_workflow_responses() -> dict[str, dict[str, Any]]:
        ts = get_current_timestamp_ms()
        base = {
            "feature_name": "workflow:test:v1",
            "feature_type": "real-time",
            "feature_data_type": "double",
            "query": "SELECT revenue FROM sales",
            "description": "Workflow test feature",
            "created_time": ts - 7200000,
            "created_by": "workflow_developer"
        }
        return {
            "ready_for_testing": {
                "success": True,
                "message": "Feature submitted for testing",
                "metadata": {
                    **base,
                    "status": "READY_FOR_TESTING",
                    "updated_time": ts,
                    "last_updated_by": "workflow_developer",
                    "submitted_by": "workflow_developer",
                    "submitted_time": ts
                },
                "event_timestamp": ts
            },
            "test_succeeded": {
                "success": True,
                "message": "Feature testing test_succeeded",
                "metadata": {
                    **base,
                    "status": "TEST_SUCCEEDED",
                    "updated_time": ts,
                    "last_updated_by": "automated_testing",
                    "tested_by": "automated_testing",
                    "tested_time": ts,
                    "test_result": "TEST_SUCCEEDED"
                },
                "event_timestamp": ts
            },
            "test_failed": {
                "success": True,
                "message": "Feature testing test_failed",
                "metadata": {
                    **base,
                    "status": "TEST_FAILED",
                    "updated_time": ts,
                    "last_updated_by": "automated_testing",
                    "tested_by": "automated_testing",
                    "tested_time": ts,
                    "test_result": "TEST_FAILED"
                },
                "event_timestamp": ts
            },
            "deployed": {
                "success": True,
                "message": "Feature approved and deployed",
                "metadata": {
                    **base,
                    "status": "DEPLOYED",
                    "updated_time": ts,
                    "last_updated_by": "feature_approver",
                    "approved_by": "feature_approver",
                    "approved_time": ts,
                    "deployed_by": "feature_approver",
                    "deployed_time": ts
                },
                "event_timestamp": ts
            }
        }

    @staticmethod
    def get_error_responses() -> dict[str, dict[str, Any]]:
        return {
            "duplicate": {
                "success": False,
                "message": "Feature already exists",
                "error": "Duplicate feature"
            },
            "not_found": {
                "success": False,
                "message": "Feature not found",
                "error": "Not found"
            },
            "invalid_role": {
                "success": False,
                "message": "Invalid user role",
                "error": "Role not allowed"
            }
        }

    @staticmethod
    def get_metadata_list_response(count: int = 3) -> dict[str, Any]:
        ts = get_current_timestamp_ms()
        features = [
            {
                "feature_name": f"test:feature:v{i}",
                "feature_type": "batch",
                "feature_data_type": "float",
                "query": f"SELECT value_{i} FROM table",
                "description": f"Test feature {i}",
                "status": "DRAFT",
                "created_time": ts,
                "updated_time": ts,
                "created_by": "test_developer"
            }
            for i in range(count)
        ]
        return {
            "success": True,
            "metadata": features,
            "total_count": count
        }

    @staticmethod
    def get_health_response() -> dict[str, Any]:
        return {
            "status": "healthy",
            "version": "1.0.0",
            "uptime_seconds": 12345,
            "dependencies": {"db": "ok"}
        }

    @staticmethod
    def get_feature_names_response(count: int = 5) -> dict[str, Any]:
        return {
            "available_features": [f"test:feature:v{i}" for i in range(count)],
            "count": count
        }

    @staticmethod
    def get_batch_feature_response() -> dict[str, Any]:
        ts = get_current_timestamp_ms()
        return {
            "metadata": {
                "features": [
                    "driver_hourly_stats:conv_rate:1",
                    "driver_hourly_stats:acc_rate:2",
                    "driver_hourly_stats:avg_daily_trips:3"
                ]
            },
            "results": {
                "values": [
                    {
                        "feature_type": "real-time",
                        "feature_data_type": "float",
                        "query": "SELECT conv_rate FROM driver_hourly_stats WHERE driver_id = ?",
                        "created_time": ts,
                        "updated_time": ts,
                        "deleted_time": None,
                        "created_by": "Fia",
                        "last_updated_by": "Ludy",
                        "deleted_by": None,
                        "approved_by": "Endy",
                        "status": "DEPLOYED",
                        "description": "Conversion rate for driver"
                    },
                    {
                        "feature_type": "batch",
                        "feature_data_type": "integer",
                        "query": "SELECT acc_rate FROM driver_hourly_stats WHERE driver_id = ?",
                        "created_time": ts,
                        "updated_time": ts,
                        "deleted_time": None,
                        "created_by": "Ludy",
                        "last_updated_by": "Eka",
                        "deleted_by": "Endy",
                        "approved_by": "Endy",
                        "status": "APPROVED",
                        "description": "Acceptance rate for driver"
                    },
                    {
                        "feature_type": "real-time",
                        "feature_data_type": "string",
                        "query": "SELECT avg_trips FROM driver_hourly_stats WHERE driver_id = ?",
                        "created_time": ts,
                        "updated_time": ts,
                        "deleted_time": ts,
                        "created_by": "Eka",
                        "last_updated_by": "Fia",
                        "deleted_by": "Endy",
                        "approved_by": "Endy",
                        "status": "DELETED",
                        "description": "Average daily trips"
                    }
                ],
                "messages": ["200 OK", "200 OK", "200 OK"],
                "event_timestamps": [ts, ts, ts]
            }
        }

    @staticmethod
    def get_concurrent_operation_responses(count: int = 10) -> list[dict[str, Any]]:
        return [MockResponses.get_successful_create_response(f"concurrent:feature:v{i}") for i in range(count)]


class MockValidationErrors:
    """Mock validation error responses."""

    @staticmethod
    def get_missing_field_error(field: str) -> dict[str, Any]:
        return {
            "success": False,
            "message": f"Missing required field: {field}",
            "error": "ValidationError"
        }

    @staticmethod
    def get_invalid_format_error(field: str, value: str) -> dict[str, Any]:
        return {
            "success": False,
            "message": f"Invalid format for {field}: {value}",
            "error": "ValidationError"
        }

    @staticmethod
    def get_string_length_error(field: str, min_length: int) -> dict[str, Any]:
        return {
            "success": False,
            "message": f"{field} must be at least {min_length} characters",
            "error": "ValidationError"
        }


class MockSecurityResponses:
    """Mock responses for security testing."""

    @staticmethod
    def get_injection_attempt_response() -> dict[str, Any]:
        return {
            "success": False,
            "message": "Injection attempt detected",
            "error": "SecurityError"
        }

    @staticmethod
    def get_unauthorized_access_response() -> dict[str, Any]:
        return {
            "success": False,
            "message": "Unauthorized access",
            "error": "PermissionDenied"
        }

    @staticmethod
    def get_rate_limit_response() -> dict[str, Any]:
        return {
            "success": False,
            "message": "Rate limit exceeded",
            "error": "RateLimit"
        }


COMMON_SUCCESS_PATTERNS = {
    "create": MockResponses.get_successful_create_response(),
    "update": MockResponses.get_successful_update_response(),
    "workflow": MockResponses.get_workflow_responses(),
    "health": MockResponses.get_health_response()
}

COMMON_ERROR_PATTERNS = MockResponses.get_error_responses()

VALIDATION_ERROR_PATTERNS = {
    "missing_name": MockValidationErrors.get_missing_field_error("feature_name"),
    "missing_type": MockValidationErrors.get_missing_field_error("feature_type"),
    "empty_name": MockValidationErrors.get_string_length_error("feature_name", 1),
    "invalid_format": MockValidationErrors.get_invalid_format_error("feature_name", "invalid_format")
}

SECURITY_RESPONSE_PATTERNS = {
    "injection": MockSecurityResponses.get_injection_attempt_response(),
    "unauthorized": MockSecurityResponses.get_unauthorized_access_response(),
    "rate_limit": MockSecurityResponses.get_rate_limit_response()
}
