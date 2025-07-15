from typing import Any


# Test data generator
class TestDataGenerator:
    # Create sample feature
    @staticmethod
    def create_sample_feature(
        name: str = "test:sample:v1",
        feature_type: str = "batch",
        data_type: str = "float",
    ) -> dict[str, Any]:
        return {
            "feature_name": name,
            "feature_type": feature_type,
            "feature_data_type": data_type,
            "query": f"SELECT value FROM {name.split(':')[0]}_table",
            "description": f"Test feature for {name}",
            "created_by": "test_developer",
            "user_role": "developer",
        }

    # Create batch features
    @staticmethod
    def create_batch_features(count: int = 5) -> list[dict[str, Any]]:
        features = []
        for i in range(count):
            features.append(
                {
                    "feature_name": f"batch:feature:v{i}",
                    "feature_type": "batch",
                    "feature_data_type": "float",
                    "query": f"SELECT value_{i} FROM batch_table",
                    "description": f"Batch test feature {i}",
                    "created_by": "batch_user",
                    "user_role": "developer",
                }
            )
        return features

    # Create edge case features
    @staticmethod
    def create_edge_case_features() -> list[dict[str, Any]]:
        return [
            {
                "feature_name": "very:long:feature:name:that:tests:boundaries:v1",
                "feature_type": "batch",
                "feature_data_type": "string",
                "query": "SELECT very_long_field_name FROM very_long_table",
                "description": "Very long description " * 10,
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

    # Create invalid feature data
    @staticmethod
    def create_invalid_feature_data() -> list[dict[str, Any]]:
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
