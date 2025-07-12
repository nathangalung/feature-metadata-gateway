"""Test data generators and sample data."""

from typing import Any


class TestDataGenerator:
    """Generate test data for scenarios."""

    @staticmethod
    def create_sample_feature_data(
        name: str = "test:sample:v1",
        feature_type: str = "batch",
        data_type: str = "float",
    ) -> dict[str, Any]:
        """Create sample feature metadata."""
        return {
            "feature_name": name,
            "feature_type": feature_type,
            "feature_data_type": data_type,
            "query": f"SELECT value FROM {name.split(':')[0]}_table",
            "description": f"Test feature for {name}",
            "created_by": "test_developer",
            "user_role": "developer",
        }

    @staticmethod
    def create_batch_features(
        count: int = 10, prefix: str = "batch"
    ) -> list[dict[str, Any]]:
        """Create multiple test features."""
        features = []
        feature_types = ["batch", "real-time", "compute-first"]
        data_types = [
            "int",
            "float",
            "string",
            "boolean",
            "double",
            "bigint",
            "decimal",
        ]
        for i in range(count):
            features.append(
                {
                    "feature_name": f"{prefix}:feature:v{i}",
                    "feature_type": feature_types[i % len(feature_types)],
                    "feature_data_type": data_types[i % len(data_types)],
                    "query": f"SELECT value_{i} FROM {prefix}_table",
                    "description": f"{prefix.capitalize()} test feature {i}",
                    "created_by": f"{prefix}_user",
                    "user_role": "developer",
                }
            )
        return features

    @staticmethod
    def create_edge_case_features() -> list[dict[str, Any]]:
        """Create edge case test features."""
        return [
            {
                "feature_name": "very:long:feature:name:that:tests:boundaries:v1",
                "feature_type": "batch",
                "feature_data_type": "string",
                "query": "SELECT very_long_field_name_for_testing FROM very_long_table_name",
                "description": "Very long description " * 50,
                "created_by": "edge_case_developer",
                "user_role": "developer",
            },
            {
                "feature_name": "special:chars:v1",
                "feature_type": "real-time",
                "feature_data_type": "string",
                "query": "SELECT field FROM table WHERE condition = 'test'",
                "description": "Test with special chars: àáâãäå ñ 中文 🚀",
                "created_by": "special_developer",
                "user_role": "developer",
            },
            {
                "feature_name": "a:b:v1",
                "feature_type": "batch",
                "feature_data_type": "int",
                "query": "SELECT 1",
                "description": "Minimal",
                "created_by": "min_dev",
                "user_role": "developer",
            },
        ]

    @staticmethod
    def create_performance_test_features(count: int = 100) -> list[dict[str, Any]]:
        """Create features for performance testing."""
        features = []
        for i in range(count):
            features.append(
                {
                    "feature_name": f"perf:test:v{i}",
                    "feature_type": "batch" if i % 2 == 0 else "real-time",
                    "feature_data_type": "float" if i % 3 == 0 else "integer",
                    "query": f"SELECT value_{i} FROM perf_table",
                    "description": f"Performance test feature {i}",
                    "created_by": "perf_tester",
                    "user_role": "developer",
                }
            )
        return features

    @staticmethod
    def create_workflow_test_data() -> dict[str, dict[str, Any]]:
        """Create data for workflow testing."""
        base_feature = {
            "feature_name": "workflow:test:v1",
            "feature_type": "real-time",
            "feature_data_type": "double",
            "query": "SELECT revenue FROM sales WHERE date >= NOW() - INTERVAL 1 DAY",
            "description": "Workflow test feature for revenue calculation",
            "created_by": "workflow_developer",
            "user_role": "developer",
        }
        return {
            "create": base_feature,
            "update": {
                "feature_name": "workflow:test:v1",
                "description": "Updated workflow test feature description",
                "last_updated_by": "workflow_developer",
                "user_role": "developer",
            },
            "ready_test": {
                "feature_name": "workflow:test:v1",
                "submitted_by": "workflow_developer",
                "user_role": "developer",
            },
            "test_success": {
                "feature_name": "workflow:test:v1",
                "test_result": "TEST_SUCCEEDED",
                "tested_by": "automated_testing",
                "user_role": "external_testing_system",
                "test_notes": "All validation tests passed successfully",
            },
            "test_failure": {
                "feature_name": "workflow:test:v1",
                "test_result": "TEST_FAILED",
                "tested_by": "automated_testing",
                "user_role": "external_testing_system",
                "test_notes": "Schema validation failed on field types",
            },
            "fix": {
                "feature_name": "workflow:test:v1",
                "fixed_by": "workflow_developer",
                "user_role": "developer",
                "fix_description": "Fixed schema validation issues",
            },
            "approve": {
                "feature_name": "workflow:test:v1",
                "approved_by": "feature_approver",
                "user_role": "approver",
                "approval_notes": "Feature approved for production deployment",
            },
            "reject": {
                "feature_name": "workflow:test:v1",
                "rejected_by": "feature_approver",
                "user_role": "approver",
                "rejection_reason": "Feature does not meet production requirements",
            },
        }

    @staticmethod
    def create_security_test_data() -> dict[str, list[str]]:
        """Create data for security testing."""
        return {
            "sql_injection": [
                "'; DROP TABLE users; --",
                "' OR '1'='1",
                "UNION SELECT * FROM passwords",
                "'; INSERT INTO admin VALUES ('hacker'); --",
            ],
            "xss_payloads": [
                "<script>alert('xss')</script>",
                "javascript:alert('xss')",
                "<img src=x onerror=alert('xss')>",
                "<svg onload=alert('xss')>",
            ],
            "command_injection": ["; ls -la", "| cat /etc/passwd", "& whoami", "`id`"],
            "path_traversal": [
                "../../../etc/passwd",
                "..\\..\\..\\windows\\system32\\config\\sam",
                "/etc/shadow",
                "../../../../etc/hosts",
            ],
        }

    @staticmethod
    def create_invalid_feature_data() -> list[dict[str, Any]]:
        """Create invalid feature data for validation testing."""
        return [
            {
                "feature_name": "",
                "feature_type": "batch",
                "feature_data_type": "float",
                "query": "",
                "description": "",
                "created_by": "",
                "user_role": "developer",
            },
            {
                "feature_name": "invalid:name",
                "feature_type": "invalid_type",
                "feature_data_type": "invalid_data_type",
                "query": "DROP TABLE users",
                "description": "<script>alert('xss')</script>",
                "created_by": "user",
                "user_role": "invalid_role",
            },
        ]


class SampleDataLoader:
    """Load and manage sample data."""

    @staticmethod
    def get_sample_metadata() -> dict[str, Any]:
        """Return sample metadata."""
        return {
            "driver_hourly_stats:conv_rate:1": {
                "feature_type": "real-time",
                "feature_data_type": "float",
                "query": "SELECT conv_rate FROM driver_hourly_stats WHERE driver_id = ?",
                "created_time": 1751429485000,
                "updated_time": 1751429485000,
                "deleted_time": None,
                "created_by": "Fia",
                "last_updated_by": "Ludy",
                "deleted_by": None,
                "approved_by": "Endy",
                "status": "DEPLOYED",
                "description": "Conversion rate for driver",
            },
            "driver_hourly_stats:acc_rate:2": {
                "feature_type": "batch",
                "feature_data_type": "integer",
                "query": "SELECT acc_rate FROM driver_hourly_stats WHERE driver_id = ?",
                "created_time": 1641081600000,
                "updated_time": 1751429485000,
                "deleted_time": None,
                "created_by": "Ludy",
                "last_updated_by": "Eka",
                "deleted_by": "Endy",
                "approved_by": "Endy",
                "status": "APPROVED",
                "description": "Acceptance rate for driver",
            },
            "driver_hourly_stats:avg_daily_trips:3": {
                "feature_type": "real-time",
                "feature_data_type": "string",
                "query": "SELECT avg_trips FROM driver_hourly_stats WHERE driver_id = ?",
                "created_time": 1751429485000,
                "updated_time": 1751429485000,
                "deleted_time": 1751429485000,
                "created_by": "Eka",
                "last_updated_by": "Fia",
                "deleted_by": "Endy",
                "approved_by": "Endy",
                "status": "DELETED",
                "description": "Average daily trips",
            },
        }

    @staticmethod
    def save_sample_data_to_file(filepath: str) -> None:
        """Save sample data to file."""
        import json

        data = SampleDataLoader.get_sample_metadata()
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def load_sample_data_from_file(filepath: str) -> dict[str, Any]:
        """Load sample data from file."""
        import json

        with open(filepath) as f:
            return json.load(f)


SAMPLE_FEATURES = TestDataGenerator.create_batch_features(5, "sample")
EDGE_CASE_FEATURES = TestDataGenerator.create_edge_case_features()
PERFORMANCE_FEATURES = TestDataGenerator.create_performance_test_features(50)
WORKFLOW_DATA = TestDataGenerator.create_workflow_test_data()
SECURITY_DATA = TestDataGenerator.create_security_test_data()
INVALID_DATA = TestDataGenerator.create_invalid_feature_data()
