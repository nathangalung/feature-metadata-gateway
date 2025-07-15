from app.models.entity import (
    FeatureMetadataBatchResponse,
    FeatureMetadataEntity,
    FeatureMetadataSingleResponse,
)


class TestFeatureMetadataEntity:
    def test_valid(self):
        entity = FeatureMetadataEntity(
            feature_name="test:feature:v1",
            feature_type="batch",
            feature_data_type="float",
            query="SELECT 1",
            description="desc",
            status="DRAFT",
            created_time=1,
            updated_time=2,
            created_by="dev",
        )
        assert entity.feature_name == "test:feature:v1"
        assert entity.status == "DRAFT"

    def test_optional(self):
        entity = FeatureMetadataEntity(
            feature_name="test:feature:v1",
            feature_type="batch",
            feature_data_type="float",
            query="SELECT 1",
            description="desc",
            status="DRAFT",
            created_time=1,
            updated_time=2,
            created_by="dev",
            last_updated_by=None,
        )
        assert entity.last_updated_by is None


class TestFeatureMetadataSingleResponse:
    def test_valid(self):
        resp = FeatureMetadataSingleResponse(
            values={"feature_type": "batch"},
            status="200 OK",
            event_timestamp=1234567890,
        )
        assert resp.status == "200 OK"
        assert isinstance(resp.values, dict)


class TestFeatureMetadataBatchResponse:
    def test_valid(self):
        resp = FeatureMetadataBatchResponse(
            metadata={"features": ["f1", "f2"]},
            results={
                "values": [{"feature_type": "batch"}, {"feature_type": "real-time"}],
                "status/message": ["200 OK", "200 OK"],
                "event_timestamp": [123, 456],
            },
        )
        assert "features" in resp.metadata
        assert isinstance(resp.results["values"], list)
