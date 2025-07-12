"""Test configuration and fixtures."""

import json
import os
import tempfile
from pathlib import Path
from typing import Any

import pytest

from app.services.feature_service import FeatureMetadataService
from app.utils.timestamp import get_current_timestamp_ms


@pytest.fixture
def sample_timestamp():
    """Sample timestamp for tests."""
    return get_current_timestamp_ms()


@pytest.fixture
def sample_feature_metadata(sample_timestamp):
    """Sample feature metadata."""
    return {
        "feature_name": "test:fixture:v1",
        "feature_type": "batch",
        "feature_data_type": "float",
        "query": "SELECT value FROM test_table",
        "description": "Test fixture feature",
        "status": "DRAFT",
        "created_time": sample_timestamp,
        "updated_time": sample_timestamp,
        "created_by": "test_user",
    }


@pytest.fixture
def sample_create_request():
    """Sample create request."""
    return {
        "feature_name": "test:create:v1",
        "feature_type": "batch",
        "feature_data_type": "float",
        "query": "SELECT value FROM test_table",
        "description": "Test create feature",
        "created_by": "test_user",
        "user_role": "developer",
    }


@pytest.fixture
def multiple_feature_data(sample_timestamp):
    """Multiple feature data."""
    return [
        {
            "feature_name": "test:multi1:v1",
            "feature_type": "batch",
            "feature_data_type": "float",
            "query": "SELECT value1 FROM table",
            "description": "Multi test feature 1",
            "status": "DRAFT",
            "created_time": sample_timestamp,
            "updated_time": sample_timestamp,
            "created_by": "test_user",
        },
        {
            "feature_name": "test:multi2:v1",
            "feature_type": "real-time",
            "feature_data_type": "integer",
            "query": "SELECT value2 FROM table",
            "description": "Multi test feature 2",
            "status": "READY_FOR_TESTING",
            "created_time": sample_timestamp,
            "updated_time": sample_timestamp,
            "created_by": "test_user",
        },
    ]


@pytest.fixture
def temp_service():
    """Temporary feature service."""
    temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
    temp_path = Path(temp_file.name)
    temp_file.close()
    service = FeatureMetadataService(str(temp_path))
    yield service
    if temp_path.exists():
        temp_path.unlink()


@pytest.fixture
def service_with_data(temp_service, sample_feature_metadata):
    """Service with test data."""
    temp_service.metadata = {
        sample_feature_metadata["feature_name"]: sample_feature_metadata
    }
    temp_service._save_data()
    return temp_service


@pytest.fixture
def service_with_multiple_features(temp_service, multiple_feature_data):
    """Service with multiple features."""
    for feature_data in multiple_feature_data:
        temp_service.metadata[feature_data["feature_name"]] = feature_data
    temp_service._save_data()
    return temp_service


TEST_FEATURES = [
    "driver_hourly_stats:conv_rate:1",
    "driver_hourly_stats:acc_rate:2",
    "driver_hourly_stats:avg_daily_trips:3",
    "customer_hourly_stats:income:1",
    "fraud_detection:amount:1",
]

TEST_ENTITIES = {"cust_no": ["X123456", "Y789012"], "driver_id": ["D001", "D002"]}

VALID_FEATURE_TYPES = ["batch", "real-time", "compute-first"]
VALID_DATA_TYPES = [
    "string",
    "float",
    "integer",
    "boolean",
    "double",
    "bigint",
    "int",
    "decimal",
]
VALID_USER_ROLES = ["developer", "external_testing_system", "approver"]
VALID_STATUSES = [
    "DRAFT",
    "READY_FOR_TESTING",
    "TEST_SUCCEEDED",
    "TEST_FAILED",
    "DEPLOYED",
    "DELETED",
]


@pytest.fixture
def sample_feature_value():
    """Sample feature value."""
    return {
        "feature_name": "test:value:v1",
        "value": 42.5,
        "feature_type": "batch",
        "feature_data_type": "float",
        "description": "Test feature value",
        "timestamp": get_current_timestamp_ms(),
        "entity_id": "test_entity_123",
    }


@pytest.fixture
def sample_batch_request():
    """Sample batch request."""
    return {
        "entity_type": "customer",
        "entity_ids": ["CUST001", "CUST002"],
        "feature_names": ["customer:income:v1", "customer:age:v1"],
        "timestamp": get_current_timestamp_ms(),
    }


@pytest.fixture
def sample_entity_request():
    """Sample entity request."""
    return {
        "entity_type": "customer",
        "entity_id": "CUST001",
        "feature_names": ["customer:income:v1", "customer:age:v1"],
        "timestamp": get_current_timestamp_ms(),
    }


@pytest.fixture
def clean_data_file():
    """Clean temporary data file."""
    temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
    temp_path = Path(temp_file.name)
    with open(temp_path, "w") as f:
        json.dump({}, f)
    yield str(temp_path)
    if temp_path.exists():
        temp_path.unlink()


@pytest.fixture(autouse=True)
def reset_test_data():
    """Reset test data before each test."""
    yield


@pytest.fixture(scope="session")
def test_config():
    """Test configuration."""
    return {
        "test_mode": True,
        "debug": True,
        "log_level": "DEBUG",
        "database_url": "sqlite:///:memory:",
        "cache_enabled": False,
    }


@pytest.fixture
def mock_current_timestamp():
    """Mock timestamp for tests."""
    return 1640995200000


@pytest.fixture
def feature_builder():
    """Feature builder for tests."""

    class FeatureBuilder:
        def __init__(self):
            self.data = {
                "feature_name": "test:builder:v1",
                "feature_type": "batch",
                "feature_data_type": "float",
                "query": "SELECT value FROM table",
                "description": "Builder test feature",
                "status": "DRAFT",
                "created_time": get_current_timestamp_ms(),
                "updated_time": get_current_timestamp_ms(),
                "created_by": "test_user",
                "last_updated_by": None,
            }

        def with_name(self, name: str):
            self.data["feature_name"] = name
            return self

        def with_type(self, feature_type: str):
            self.data["feature_type"] = feature_type
            return self

        def with_status(self, status: str):
            self.data["status"] = status
            return self

        def with_data_type(self, data_type: str):
            self.data["feature_data_type"] = data_type
            return self

        def build(self) -> dict[str, Any]:
            return self.data.copy()

    return FeatureBuilder()


@pytest.fixture
def validation_test_cases():
    """Validation test cases."""
    return {
        "valid_feature_names": [
            "driver:conv_rate:v1",
            "customer:income:v2",
            "fraud:score:v10",
        ],
        "invalid_feature_names": [
            "invalid_name",
            "123:invalid:v1",
            "feature:name",
            "feature:name:invalid",
        ],
        "valid_queries": [
            "SELECT value FROM table",
            "SELECT COUNT(*) as count FROM users WHERE active = 1",
            "SELECT avg(price) FROM products",
        ],
        "invalid_queries": [
            "",
            "DROP TABLE users",
            "SELECT * FROM users; DELETE FROM users",
            "<script>alert('xss')</script>",
        ],
        "valid_descriptions": [
            "This is a valid description for testing",
            "Feature calculates customer conversion rate over time",
            "Real-time fraud detection score based on transaction patterns",
        ],
        "invalid_descriptions": [
            "",
            "Short",
            "<script>alert('xss')</script>",
            "a" * 1001,
        ],
    }


@pytest.fixture
def workflow_test_data():
    """Workflow test data."""
    return {
        "developer_actions": [
            {"action": "create", "should_succeed": True},
            {"action": "update", "should_succeed": True},
            {"action": "delete", "should_succeed": True},
            {"action": "ready_for_testing", "should_succeed": True},
            {"action": "approve", "should_succeed": False},
            {"action": "test", "should_succeed": False},
        ],
        "external_testing_system_actions": [
            {"action": "create", "should_succeed": False},
            {"action": "update", "should_succeed": False},
            {"action": "test", "should_succeed": True},
            {"action": "approve", "should_succeed": False},
        ],
        "approver_actions": [
            {"action": "create", "should_succeed": False},
            {"action": "approve", "should_succeed": True},
            {"action": "reject", "should_succeed": True},
            {"action": "test", "should_succeed": False},
        ],
    }


@pytest.fixture
def performance_test_data():
    """Performance test data."""
    features = []
    for i in range(100):
        features.append(
            {
                "feature_name": f"perf:test:v{i}",
                "feature_type": "batch" if i % 2 == 0 else "real-time",
                "feature_data_type": "float" if i % 3 == 0 else "integer",
                "query": f"SELECT value_{i} FROM table_{i}",
                "description": f"Performance test feature {i}",
                "status": "DRAFT",
                "created_time": get_current_timestamp_ms(),
                "updated_time": get_current_timestamp_ms(),
                "created_by": "perf_tester",
            }
        )
    return features


@pytest.fixture
def security_test_cases():
    """Security test cases."""
    return {
        "sql_injection_attempts": [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "UNION SELECT password FROM users",
            "'; EXEC xp_cmdshell('dir'); --",
        ],
        "xss_attempts": [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<iframe src='javascript:alert(1)'></iframe>",
            "<img onerror='alert(1)' src='x'>",
        ],
        "path_traversal_attempts": [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32",
            "/etc/shadow",
            "c:\\windows\\system.ini",
        ],
    }


@pytest.fixture
def edge_case_test_data():
    """Edge case test data."""
    return {
        "empty_values": [None, "", " ", "\t", "\n"],
        "very_long_strings": {
            "description": "a" * 1001,
            "query": "SELECT " + "a" * 5001,
            "feature_name": "a" * 256,
        },
        "special_characters": {
            "unicode": "测试特征名称",
            "symbols": "!@#$%^&*()_+-=[]{}|;:'\",.<>?",
            "emojis": "🚀📊💡🔧⚡",
        },
        "boundary_timestamps": [0, 1, 946684800000, 2147483647000, -1, -1000],
    }


@pytest.fixture(autouse=True, scope="class")
def clean_feature_metadata_file():
    """Clean feature metadata file before each test class."""
    file_path = "data/feature_metadata.json"
    if os.path.exists(file_path):
        os.remove(file_path)
    yield
    if os.path.exists(file_path):
        os.remove(file_path)
