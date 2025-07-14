import pytest
from pydantic import ValidationError

from app.models.entity import (
    BatchFeatureRequest,
    BatchFeatureResponse,
    FeatureEntity,
    FeatureValue,
)


class TestFeatureEntity:
    """Test FeatureEntity model."""

    # Valid entity creation
    def test_valid_feature_entity(self):
        entity = FeatureEntity(
            features=["driver_hourly_stats:conv_rate:1", "fraud:amount:v1"],
            entities={"driver_id": ["123", "456"], "user_id": ["789"]},
            event_timestamp=1640995200000,
        )
        assert len(entity.features) == 2
        assert "driver_id" in entity.entities
        assert entity.event_timestamp == 1640995200000

    # Empty features list
    def test_empty_features_list(self):
        entity = FeatureEntity(
            features=[], entities={"driver_id": ["123"]}, event_timestamp=1640995200000
        )
        assert entity.features == []

    # Missing required fields
    def test_missing_required_fields(self):
        with pytest.raises(ValidationError):
            FeatureEntity(
                features=["test:feature:v1"]
                # Missing entities and event_timestamp
            )


class TestBatchFeatureRequest:
    """Test BatchFeatureRequest model."""

    # Valid batch request
    def test_valid_batch_request(self):
        request = BatchFeatureRequest(
            features=["driver_hourly_stats:conv_rate:1", "fraud:detection:v2"],
            entities={"driver_id": ["D123", "D456"], "transaction_id": ["T789"]},
            event_timestamp=1640995200000,
        )
        assert len(request.features) == 2
        assert len(request.entities["driver_id"]) == 2
        assert request.event_timestamp == 1640995200000

    # Optional event timestamp
    def test_optional_timestamp(self):
        request = BatchFeatureRequest(
            features=["test:feature:v1"], entities={"user_id": ["U123"]}
        )
        assert request.event_timestamp is None

    # Complex entities structure
    def test_complex_entities_structure(self):
        request = BatchFeatureRequest(
            features=["customer:profile:v1"],
            entities={
                "customer_id": ["C001", "C002", "C003"],
                "region_id": ["R001"],
                "product_id": ["P001", "P002"],
            },
            event_timestamp=1640995200000,
        )
        assert len(request.entities) == 3
        assert len(request.entities["customer_id"]) == 3
        assert len(request.entities["region_id"]) == 1


class TestFeatureValue:
    """Test FeatureValue model."""

    # Complete feature value
    def test_complete_feature_value(self):
        feature_value = FeatureValue(
            feature_type="real-time",
            feature_data_type="double",
            query="SELECT revenue FROM sales WHERE id = %s",
            created_time=1640995200000,
            updated_time=1640995800000,
            created_by="data_engineer",
            last_updated_by="data_scientist",
            approved_by="feature_approver",
            status="DEPLOYED",
            description="Real-time revenue calculation feature",
        )
        assert feature_value.feature_type == "real-time"
        assert feature_value.approved_by == "feature_approver"
        assert feature_value.status == "DEPLOYED"

    # Minimal feature value
    def test_minimal_feature_value(self):
        feature_value = FeatureValue(
            feature_type="batch",
            feature_data_type="int",
            query="SELECT count(*) FROM users",
            created_time=1640995200000,
            updated_time=1640995200000,
            created_by="developer",
            last_updated_by="developer",
            status="DRAFT",
            description="User count feature",
        )
        assert feature_value.approved_by is None

    # Different feature/data types
    def test_feature_value_types(self):
        types_combinations = [
            ("batch", "int"),
            ("real-time", "float"),
            ("compute-first", "string"),
            ("batch", "boolean"),
            ("real-time", "double"),
            ("compute-first", "bigint"),
            ("batch", "decimal"),
        ]
        for feature_type, data_type in types_combinations:
            feature_value = FeatureValue(
                feature_type=feature_type,
                feature_data_type=data_type,
                query=f"SELECT value FROM {feature_type}_table",
                created_time=1640995200000,
                updated_time=1640995200000,
                created_by="test_user",
                last_updated_by="test_user",
                status="DRAFT",
                description=f"Test {feature_type} {data_type} feature",
            )
            assert feature_value.feature_type == feature_type
            assert feature_value.feature_data_type == data_type


class TestBatchFeatureResponse:
    """Test BatchFeatureResponse model."""

    # Valid batch response
    def test_valid_batch_response(self):
        feature_value = FeatureValue(
            feature_type="batch",
            feature_data_type="float",
            query="SELECT avg_score FROM metrics",
            created_time=1640995200000,
            updated_time=1640995200000,
            created_by="metrics_team",
            last_updated_by="metrics_team",
            status="DEPLOYED",
            description="Average score calculation",
        )
        response = BatchFeatureResponse(results=[feature_value])
        assert isinstance(response.results, list)

    # Multiple results
    def test_multiple_results(self):
        feature_value1 = FeatureValue(
            feature_type="batch",
            feature_data_type="int",
            query="SELECT count FROM table1",
            created_time=1640995200000,
            updated_time=1640995200000,
            created_by="team1",
            last_updated_by="team1",
            status="DEPLOYED",
            description="Count feature 1",
        )
        feature_value2 = FeatureValue(
            feature_type="real-time",
            feature_data_type="string",
            query="SELECT name FROM table2",
            created_time=1640995200000,
            updated_time=1640995200000,
            created_by="team2",
            last_updated_by="team2",
            status="DEPLOYED",
            description="Name feature 2",
        )
        response = BatchFeatureResponse(results=[feature_value1, feature_value2])
        assert isinstance(response.results, list)
        assert len(response.results) == 2

    # Mixed result types
    def test_mixed_result_types(self):
        feature_value = FeatureValue(
            feature_type="compute-first",
            feature_data_type="boolean",
            query="SELECT is_active FROM users",
            created_time=1640995200000,
            updated_time=1640995200000,
            created_by="user_team",
            last_updated_by="user_team",
            status="DEPLOYED",
            description="User active status",
        )
        with pytest.raises(ValidationError):
            BatchFeatureResponse(
                results=[feature_value, "simple_string_result", "another_string_result"]
            )

    # Empty results
    def test_empty_results(self):
        response = BatchFeatureResponse(results=[])
        assert isinstance(response.results, list)
        assert response.results == []
