import pytest

from app.services.feature_service import FeatureService
from app.utils.timestamp import get_current_timestamp_ms

# Constants
ENTITY_COUNT_2 = 2
ENTITY_COUNT_3 = 3


class TestFeatureService:
    """Test feature service functionality"""

    @pytest.fixture
    def service(self):
        """Create service instance"""
        return FeatureService()

    async def test_get_feature_metadata(self, service):
        """Test feature metadata retrieval"""
        timestamp = get_current_timestamp_ms()

        # Known feature
        metadata = await service.get_feature_metadata("driver_hourly_stats:conv_rate:1", timestamp)
        assert metadata is not None
        assert "feature_type" in metadata
        assert "feature_data_type" in metadata

        # Unknown feature
        metadata = await service.get_feature_metadata("unknown:feature:1", timestamp)
        assert metadata is None

    async def test_get_feature_value_with_metadata(self, service):
        """Test feature value with metadata"""
        timestamp = get_current_timestamp_ms()

        # Valid feature and entity
        result = await service.get_feature_value_with_metadata(
            "driver_hourly_stats:conv_rate:1", "X123456", timestamp
        )
        assert result is not None
        assert "value" in result
        assert "feature_type" in result
        assert "created_by" in result

        # Invalid feature
        result = await service.get_feature_value_with_metadata(
            "unknown:feature:1", "X123456", timestamp
        )
        assert result is None

    async def test_batch_process_features(self, service):
        """Test batch feature processing"""
        timestamp = get_current_timestamp_ms()
        features = ["driver_hourly_stats:conv_rate:1", "driver_hourly_stats:acc_rate:2"]
        entities = {"cust_no": ["X123456", "1002"]}

        result = await service.batch_process_features(features, entities, timestamp)

        assert "metadata" in result
        assert "results" in result
        assert len(result["results"]) == ENTITY_COUNT_2

        for entity_result in result["results"]:
            assert len(entity_result["values"]) == ENTITY_COUNT_3
            assert len(entity_result["statuses"]) == ENTITY_COUNT_3
            assert len(entity_result["event_timestamps"]) == ENTITY_COUNT_3

    def test_validate_feature_format(self, service):
        """Test feature format validation"""
        # Valid formats
        assert service._validate_feature_format("category:name:version")
        assert service._validate_feature_format("driver_hourly_stats:conv_rate:1")

        # Invalid formats
        assert not service._validate_feature_format("category:name")
        assert not service._validate_feature_format("category:name:version:extra")
        assert not service._validate_feature_format(":name:version")
        assert not service._validate_feature_format("category::version")

    def test_generate_feature_value_consistency(self, service):
        """Test feature value generation consistency"""
        # Should be deterministic for same inputs
        value1 = service._generate_feature_value("driver_hourly_stats:conv_rate:1", "X123456")
        value2 = service._generate_feature_value("driver_hourly_stats:conv_rate:1", "X123456")
        assert value1 == value2

        # Test different combinations give different values
        test_cases = [
            ("driver_hourly_stats:conv_rate:1", "entity_1"),
            ("driver_hourly_stats:conv_rate:1", "entity_2"),
            ("driver_hourly_stats:acc_rate:2", "entity_1"),
        ]

        values = []
        for feature, entity in test_cases:
            value = service._generate_feature_value(feature, entity)
            values.append(value)

        # At least some values should be different
        unique_values = set(str(v) for v in values)
        assert len(unique_values) > 1, "Should generate some different values"

    def test_can_edit_feature(self, service):
        """Test feature edit permissions"""
        assert service._can_edit_feature("READY FOR TESTING")
        assert service._can_edit_feature("TESTED")
        assert service._can_edit_feature("APPROVED")
        assert not service._can_edit_feature("DEPLOYED")

    def test_feature_value_types(self, service):
        """Test feature value types match data types"""
        # Float feature
        float_val = service._generate_feature_value("driver_hourly_stats:conv_rate:1", "X123456")
        assert isinstance(float_val, float)

        # Integer feature
        int_val = service._generate_feature_value("driver_hourly_stats:acc_rate:2", "X123456")
        assert isinstance(int_val, int)

        # String feature
        str_val = service._generate_feature_value(
            "driver_hourly_stats:avg_daily_trips:3", "X123456"
        )
        assert isinstance(str_val, str)

    def test_available_features(self, service):
        """Test available features list"""
        features = service.get_available_features()
        assert isinstance(features, list)
        assert len(features) > 0
        assert "driver_hourly_stats:conv_rate:1" in features
