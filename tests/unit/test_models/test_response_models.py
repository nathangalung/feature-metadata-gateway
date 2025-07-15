from app.models.response import (
    FeatureMetadataBatchResponse,
    FeatureMetadataSingleResponse,
)


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
