import pytest
from pydantic import ValidationError

from app.models.request import BatchFeatureResult, FeatureMetadata
from app.models.response import AllMetadataResponse, StatusListResponse


class TestFeatureMetadata:
    """Test FeatureMetadata model."""

    # Complete metadata
    def test_complete_metadata(self):
        metadata = FeatureMetadata(
            feature_name="test:complete:v1",
            feature_type="real-time",
            feature_data_type="double",
            query="SELECT revenue FROM sales",
            description="Complete test feature",
            status="DEPLOYED",
            created_time=1640995200000,
            updated_time=1640996100000,
            created_by="developer",
            last_updated_by="maintainer",
            approved_by="approver",
            approved_time=1640996000000,
            deployed_by="deployer",
            deployed_time=1640996050000,
            tested_by="tester",
            tested_time=1640995900000,
            test_result="TEST_SUCCEEDED",
            submitted_by="submitter",
            submitted_time=1640995800000,
        )
        assert metadata.feature_name == "test:complete:v1"
        assert metadata.status == "DEPLOYED"
        assert metadata.approved_by == "approver"
        assert metadata.test_result == "TEST_SUCCEEDED"

    # Minimal metadata
    def test_minimal_metadata(self):
        metadata = FeatureMetadata(
            feature_name="test:minimal:v1",
            feature_type="batch",
            feature_data_type="int",
            query="SELECT count FROM table",
            description="Minimal test feature",
            status="DRAFT",
            created_time=1640995200000,
            updated_time=1640995200000,
            created_by="developer",
            last_updated_by="developer",
        )
        assert metadata.approved_by is None
        assert metadata.tested_by is None
        assert metadata.deployed_by is None

    # Status progression
    def test_status_progression(self):
        statuses = [
            "DRAFT",
            "READY_FOR_TESTING",
            "TEST_SUCCEEDED",
            "TEST_FAILED",
            "DEPLOYED",
            "DEPRECATED",
        ]
        for status in statuses:
            metadata = FeatureMetadata(
                feature_name=f"test:status:{status.lower()}:v1",
                feature_type="batch",
                feature_data_type="string",
                query="SELECT name FROM table",
                description=f"Test feature with {status} status",
                status=status,
                created_time=1640995200000,
                updated_time=1640995200000,
                created_by="developer",
                last_updated_by="developer",
            )
            assert metadata.status == status


class TestBatchFeatureResult:
    """Test BatchFeatureResult."""

    # Multiple features response
    def test_multiple_features_response(self):
        values = [
            {
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
            {
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
            {
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
        ]
        messages = ["200 OK", "200 OK", "200 OK"]
        event_timestamps = [1751429485000, 1751429485000, 1751429485000]

        result = BatchFeatureResult(
            values=values, messages=messages, event_timestamps=event_timestamps
        )
        assert len(result.values) == 3
        assert result.messages == messages
        assert result.event_timestamps == event_timestamps

    # Single feature response
    def test_single_feature_response(self):
        values = [
            {
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
            }
        ]
        messages = ["200 OK"]
        event_timestamps = [1751429485000]

        result = BatchFeatureResult(
            values=values, messages=messages, event_timestamps=event_timestamps
        )
        assert len(result.values) == 1
        assert result.messages == ["200 OK"]
        assert result.event_timestamps == [1751429485000]

    # Invalid batch feature result
    def test_invalid_batch_feature_result(self):
        with pytest.raises(ValidationError):
            BatchFeatureResult()


class TestAllMetadataResponse:
    """Test AllMetadataResponse."""

    # Multiple metadata response
    def test_multiple_metadata_response(self):
        metadata_list = []
        for i in range(3):
            metadata_list.append(
                FeatureMetadata(
                    feature_name=f"test:multi:v{i}",
                    feature_type="batch" if i % 2 == 0 else "real-time",
                    feature_data_type="float",
                    query=f"SELECT value_{i} FROM table_{i}",
                    description=f"Multi test feature {i}",
                    status="DEPLOYED" if i == 0 else "DRAFT",
                    created_time=1640995200000 + i * 1000,
                    updated_time=1640995200000 + i * 1000,
                    created_by=f"developer_{i}",
                    last_updated_by=f"developer_{i}",
                )
            )
        response = AllMetadataResponse(metadata=metadata_list, total_count=3)
        assert len(response.metadata) == 3
        assert response.total_count == 3
        assert response.metadata[0].feature_name == "test:multi:v0"
        assert response.metadata[2].feature_name == "test:multi:v2"

    # Empty metadata response
    def test_empty_metadata_response(self):
        response = AllMetadataResponse(metadata=[], total_count=0)
        assert response.metadata == []
        assert response.total_count == 0

    # Large metadata response
    def test_large_metadata_response(self):
        metadata_list = []
        for i in range(100):
            metadata_list.append(
                FeatureMetadata(
                    feature_name=f"test:large:v{i}",
                    feature_type="batch",
                    feature_data_type="int",
                    query=f"SELECT count_{i} FROM large_table",
                    description=f"Large test feature {i}",
                    status="DRAFT",
                    created_time=1640995200000,
                    updated_time=1640995200000,
                    created_by="bulk_creator",
                    last_updated_by="bulk_creator",
                )
            )
        response = AllMetadataResponse(metadata=metadata_list, total_count=100)
        assert len(response.metadata) == 100
        assert response.total_count == 100
        assert all(meta.created_by == "bulk_creator" for meta in response.metadata)

    # Filtered metadata response
    def test_filtered_metadata_response(self):
        deployed_metadata = [
            FeatureMetadata(
                feature_name="test:deployed:v1",
                feature_type="real-time",
                feature_data_type="string",
                query="SELECT name FROM users",
                description="Deployed feature 1",
                status="DEPLOYED",
                created_time=1640995200000,
                updated_time=1640995200000,
                created_by="developer",
                last_updated_by="developer",
                approved_by="approver",
                deployed_by="deployer",
            ),
            FeatureMetadata(
                feature_name="test:deployed:v2",
                feature_type="batch",
                feature_data_type="double",
                query="SELECT revenue FROM sales",
                description="Deployed feature 2",
                status="DEPLOYED",
                created_time=1640995200000,
                updated_time=1640995200000,
                created_by="developer",
                last_updated_by="developer",
                approved_by="approver",
                deployed_by="deployer",
            ),
        ]
        response = AllMetadataResponse(metadata=deployed_metadata, total_count=2)
        assert all(meta.status == "DEPLOYED" for meta in response.metadata)
        assert all(meta.approved_by == "approver" for meta in response.metadata)
        assert response.total_count == 2

    # Dict metadata input
    def test_dict_metadata_input(self):
        meta_dict = {
            "f1": FeatureMetadata(
                feature_name="f1",
                feature_type="batch",
                feature_data_type="int",
                query="SELECT 1",
                description="desc",
                status="DRAFT",
                created_time=1,
                updated_time=2,
                created_by="dev",
            ),
            "f2": FeatureMetadata(
                feature_name="f2",
                feature_type="batch",
                feature_data_type="int",
                query="SELECT 2",
                description="desc",
                status="DRAFT",
                created_time=1,
                updated_time=2,
                created_by="dev",
            ),
        }
        resp = AllMetadataResponse(metadata=meta_dict)
        assert isinstance(resp.metadata, list)
        assert resp.total_count == 2

    # Validator metadata
    def test_validator_metadata(self):
        meta_dict = {
            "f1": FeatureMetadata(
                feature_name="f1",
                feature_type="batch",
                feature_data_type="int",
                query="SELECT 1",
                description="desc",
                status="DRAFT",
                created_time=1,
                updated_time=2,
                created_by="dev",
            )
        }
        resp = AllMetadataResponse(metadata=meta_dict)
        assert isinstance(resp.metadata, list)
        resp2 = AllMetadataResponse(metadata=None)
        assert resp2.metadata == []


class TestResponseValidation:
    """Test response validation."""

    # Required fields validation
    def test_required_fields_validation(self):
        with pytest.raises(ValidationError):
            FeatureMetadata()
        with pytest.raises(ValidationError):
            BatchFeatureResult()

    # Field type validation
    def test_field_type_validation(self):
        with pytest.raises(ValidationError):
            FeatureMetadata(
                feature_name="test:invalid:v1",
                feature_type="batch",
                feature_data_type="int",
                query="SELECT 1",
                description="Invalid timestamp test",
                status="DRAFT",
                created_time="invalid_timestamp",
                updated_time=1640995200000,
                created_by="developer",
                last_updated_by="developer",
            )
        with pytest.raises(ValidationError):
            BatchFeatureResult(
                values=[{"feature_type": "real-time"}],
                messages="should_be_list",
                event_timestamps=[1751429485000],
            )

    # Optional fields handling
    def test_optional_fields_handling(self):
        metadata = FeatureMetadata(
            feature_name="test:optional:v1",
            feature_type="batch",
            feature_data_type="string",
            query="SELECT name FROM table",
            description="Optional fields test",
            status="DRAFT",
            created_time=1640995200000,
            updated_time=1640995200000,
            created_by="developer",
            last_updated_by="developer",
            approved_by=None,
            approved_time=None,
            deployed_by=None,
            deployed_time=None,
            tested_by=None,
            tested_time=None,
            test_result=None,
            submitted_by=None,
            submitted_time=None,
        )
        assert metadata.approved_by is None
        assert metadata.tested_by is None
        assert metadata.deployed_by is None


# AllMetadataResponse validator tests
def test_all_metadata_response_init_and_validator():
    meta1 = FeatureMetadata(
        feature_name="f1",
        feature_type="batch",
        feature_data_type="float",
        query="SELECT 1",
        description="desc",
        status="DRAFT",
        created_time=1,
        updated_time=2,
        created_by="dev",
    )
    meta2 = FeatureMetadata(
        feature_name="f2",
        feature_type="batch",
        feature_data_type="float",
        query="SELECT 2",
        description="desc",
        status="DRAFT",
        created_time=1,
        updated_time=2,
        created_by="dev",
    )
    resp = AllMetadataResponse(metadata={"f1": meta1, "f2": meta2})
    assert isinstance(resp.metadata, list)
    assert resp.total_count == 2
    resp2 = AllMetadataResponse(metadata=[meta1, meta2])
    assert isinstance(resp2.metadata, list)
    assert resp2.total_count == 2
    resp3 = AllMetadataResponse(metadata=None)
    assert resp3.metadata == []
    assert resp3.total_count == 0
    assert AllMetadataResponse.validate_metadata({"f1": meta1}) == [meta1]
    assert AllMetadataResponse.validate_metadata(None) == []


# StatusListResponse count tests
def test_status_list_response_init():
    resp = StatusListResponse(status="DEPLOYED", features=["a", "b", "c"])
    assert resp.count == 3
    resp2 = StatusListResponse(status="DEPLOYED", features=["a", "b"], count=5)
    assert resp2.count == 5


# AllMetadataResponse invalid metadata type
def test_all_metadata_response_invalid_metadata_type():
    resp = AllMetadataResponse(metadata=123)
    assert resp.metadata == []
    assert resp.total_count == 0
    resp2 = AllMetadataResponse(metadata="notalistordict")
    assert resp2.metadata == []
    assert resp2.total_count == 0
    resp3 = AllMetadataResponse(metadata=3.14)
    assert resp3.metadata == []
    assert resp3.total_count == 0


# AllMetadataResponse none metadata
def test_all_metadata_response_none_metadata():
    resp = AllMetadataResponse(metadata=None)
    assert resp.metadata == []
    assert resp.total_count == 0


# AllMetadataResponse no metadata key
def test_all_metadata_response_no_metadata_key():
    resp = AllMetadataResponse()
    assert resp.metadata == []
    assert resp.total_count == 0
