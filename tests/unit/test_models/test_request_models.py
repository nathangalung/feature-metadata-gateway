import pytest
from pydantic import ValidationError

from app.models.request import (
    ApproveFeatureRequest,
    BatchFeatureRequest,
    BatchFeatureResponse,
    BatchFeatureResult,
    CreateFeatureRequest,
    DeleteFeatureRequest,
    FeatureMetadata,
    FixFeatureRequest,
    GetAllFeaturesRequest,
    GetFeatureRequest,
    ReadyTestFeatureRequest,
    ReadyTestRequest,
    RejectFeatureRequest,
    TestFeatureRequest,
    UpdateFeatureRequest,
)


class TestCreateFeatureRequest:
    """Test CreateFeatureRequest."""

    # Valid request
    def test_valid_request(self):
        req = CreateFeatureRequest(
            feature_name="driver:hourly_stats:v1",
            feature_type="real-time",
            feature_data_type="float",
            query="SELECT conv_rate FROM driver_hourly_stats WHERE driver_id = ?",
            description="Conversion rate for driver",
            created_by="Fia",
            user_role="developer",
        )
        assert req.feature_name == "driver:hourly_stats:v1"

    # Missing required fields
    def test_missing_required_fields(self):
        with pytest.raises(ValidationError):
            CreateFeatureRequest(feature_name="driver:hourly_stats:v1")

    # Empty string validation
    def test_empty_string_validation(self):
        with pytest.raises(ValidationError):
            CreateFeatureRequest(
                feature_name="",
                feature_type="real-time",
                feature_data_type="float",
                query="SELECT conv_rate FROM driver_hourly_stats WHERE driver_id = ?",
                description="Conversion rate for driver",
                created_by="Fia",
                user_role="developer",
            )

    # Feature name validation
    def test_feature_name_validation(self):
        valid_names = [
            "driver:hourly_stats:v1",
            "fraud:amount:v1",
            "customer:income:v2",
        ]
        for name in valid_names:
            req = CreateFeatureRequest(
                feature_name=name,
                feature_type="real-time",
                feature_data_type="float",
                query="SELECT 1",
                description="desc",
                created_by="dev",
                user_role="developer",
            )
            assert req.feature_name == name

    # Created by validation
    def test_created_by_validation(self):
        with pytest.raises(ValidationError):
            CreateFeatureRequest(
                feature_name="driver:hourly_stats:v1",
                feature_type="real-time",
                feature_data_type="float",
                query="SELECT 1",
                description="desc",
                created_by="",
                user_role="developer",
            )

    # Description validation
    def test_description_validation(self):
        with pytest.raises(ValidationError):
            CreateFeatureRequest(
                feature_name="driver:hourly_stats:v1",
                feature_type="real-time",
                feature_data_type="float",
                query="SELECT 1",
                description="",
                created_by="dev",
                user_role="developer",
            )

    # Query validation
    def test_query_validation(self):
        with pytest.raises(ValidationError):
            CreateFeatureRequest(
                feature_name="driver:hourly_stats:v1",
                feature_type="real-time",
                feature_data_type="float",
                query="",
                description="desc",
                created_by="dev",
                user_role="developer",
            )


class TestUpdateFeatureRequest:
    """Test UpdateFeatureRequest."""

    # Partial update
    def test_partial_update(self):
        req = UpdateFeatureRequest(
            feature_name="driver:hourly_stats:v1",
            description="Updated desc",
            last_updated_by="Fia",
            user_role="developer",
        )
        assert req.description == "Updated desc"
        assert req.feature_type is None

    # All fields update
    def test_all_fields_update(self):
        req = UpdateFeatureRequest(
            feature_name="driver:hourly_stats:v1",
            feature_type="real-time",
            feature_data_type="float",
            query="SELECT conv_rate FROM driver_hourly_stats WHERE driver_id = ?",
            description="desc",
            status="READY_FOR_TESTING",
            last_updated_by="Fia",
            user_role="developer",
        )
        assert req.feature_type == "real-time"
        assert req.status == "READY_FOR_TESTING"

    # Optional fields
    def test_optional_fields(self):
        req = UpdateFeatureRequest(
            feature_name="driver:hourly_stats:v1",
            last_updated_by="Fia",
            user_role="developer",
        )
        assert req.feature_type is None
        assert req.feature_data_type is None
        assert req.query is None


class TestTestFeatureRequest:
    """Test TestFeatureRequest."""

    # Valid test success
    def test_valid_test_success(self):
        req = TestFeatureRequest(
            feature_name="driver:hourly_stats:v1",
            test_result="TEST_SUCCEEDED",
            tested_by="test_system",
            user_role="external_testing_system",
            test_notes="All tests passed",
        )
        assert req.test_result == "TEST_SUCCEEDED"

    # Valid test failure
    def test_valid_test_failure(self):
        req = TestFeatureRequest(
            feature_name="driver:hourly_stats:v1",
            test_result="TEST_FAILED",
            tested_by="test_system",
            user_role="external_testing_system",
            test_notes="Validation failed",
        )
        assert req.test_result == "TEST_FAILED"

    # Optional notes
    def test_optional_notes(self):
        req = TestFeatureRequest(
            feature_name="driver:hourly_stats:v1",
            test_result="TEST_SUCCEEDED",
            tested_by="test_system",
            user_role="external_testing_system",
        )
        assert req.test_notes is None


class TestApproveRejectRequests:
    """Test Approve/Reject requests."""

    # Approve request
    def test_approve_request(self):
        req = ApproveFeatureRequest(
            feature_name="driver:hourly_stats:v1",
            approved_by="Endy",
            user_role="approver",
            approval_notes="Approved",
        )
        assert req.approved_by == "Endy"
        assert req.approval_notes == "Approved"

    # Reject request
    def test_reject_request(self):
        req = RejectFeatureRequest(
            feature_name="driver:hourly_stats:v1",
            rejected_by="Endy",
            user_role="approver",
            rejection_reason="Not valid",
        )
        assert req.rejected_by == "Endy"
        assert req.rejection_reason == "Not valid"


class TestGetRequests:
    """Test Get requests."""

    # Get metadata request
    def test_get_metadata_request(self):
        req = GetFeatureRequest(
            feature_name="driver:hourly_stats:v1", user_role="developer"
        )
        assert req.feature_name == "driver:hourly_stats:v1"
        assert req.user_role == "developer"
        with pytest.raises(ValidationError):
            GetFeatureRequest(user_role="developer")
        with pytest.raises(ValidationError):
            GetFeatureRequest(feature_name="", user_role="developer")
        with pytest.raises(ValidationError):
            GetFeatureRequest(feature_name="invalid", user_role="developer")

    # Get all features request
    def test_get_all_features_request(self):
        req = GetAllFeaturesRequest(user_role="developer")
        assert req.status is None
        assert req.feature_type is None
        assert req.created_by is None
        assert req.limit is None
        assert req.offset is None
        assert req.user_role == "developer"
        req = GetAllFeaturesRequest(
            status="DEPLOYED",
            feature_type="batch",
            created_by="Ludy",
            limit=10,
            offset=5,
            user_role="developer",
        )
        assert req.status == "DEPLOYED"
        assert req.feature_type == "batch"
        assert req.created_by == "Ludy"
        assert req.limit == 10
        assert req.offset == 5
        assert req.user_role == "developer"


class TestDeleteReadyFixRequests:
    """Test Delete/Ready/Fix requests."""

    # Delete feature request
    def test_delete_feature_request(self):
        req = DeleteFeatureRequest(
            feature_name="driver:hourly_stats:v1",
            deleted_by="dev",
            deletion_reason="Cleanup",
            user_role="developer",
        )
        assert req.deletion_reason == "Cleanup"

    # Ready test request
    def test_ready_test_request(self):
        req = ReadyTestRequest(
            feature_name="driver:hourly_stats:v1",
            submitted_by="dev",
            user_role="developer",
        )
        assert req.submitted_by == "dev"

    # Ready test feature request
    def test_ready_test_feature_request(self):
        req = ReadyTestFeatureRequest(
            feature_name="driver:hourly_stats:v1",
            submitted_by="dev",
            user_role="developer",
        )
        assert req.submitted_by == "dev"

    # Fix feature request
    def test_fix_feature_request(self):
        req = FixFeatureRequest(
            feature_name="driver:hourly_stats:v1",
            fixed_by="dev",
            fix_description="Fixed bug",
            user_role="developer",
        )
        assert req.fix_description == "Fixed bug"


class TestBatchFeatureResultRequest:
    """Test BatchFeatureResult and related."""

    # Batch feature result
    def test_batch_feature_result(self):
        result = BatchFeatureResult(
            values=[1, 2, 3], messages=["ok", "ok", "ok"], event_timestamps=[1, 2, 3]
        )
        assert result.values == [1, 2, 3]

    # Batch feature request
    def test_batch_feature_request(self):
        req = BatchFeatureRequest(
            features=["driver:hourly_stats:v1"],
            entities={"driver_id": ["D123"]},
            event_timestamp=1640995200000,
        )
        assert req.features == ["driver:hourly_stats:v1"]
        assert req.entities["driver_id"] == ["D123"]

    # Batch feature response
    def test_batch_feature_response(self):
        result = BatchFeatureResult(
            values=[1, 2, 3], messages=["ok", "ok", "ok"], event_timestamps=[1, 2, 3]
        )
        resp = BatchFeatureResponse(
            metadata={"driver:hourly_stats:v1": {}}, results=[result]
        )
        assert isinstance(resp.results, list)


class TestFeatureMetadataModel:
    """Test FeatureMetadata model."""

    # Feature metadata model
    def test_feature_metadata_model(self):
        meta = FeatureMetadata(
            feature_name="driver:hourly_stats:v1",
            feature_type="batch",
            feature_data_type="float",
            query="SELECT 1",
            description="desc",
            status="DRAFT",
            created_time=1,
            updated_time=2,
            created_by="dev",
        )
        assert meta.feature_name == "driver:hourly_stats:v1"
        assert meta.status == "DRAFT"


# Feature name validator
def test_create_feature_request_feature_name_validator():
    with pytest.raises(ValidationError):
        CreateFeatureRequest(
            feature_name=None,
            feature_type="batch",
            feature_data_type="float",
            query="SELECT 1",
            description="desc",
            created_by="dev",
            user_role="developer",
        )
    with pytest.raises(ValidationError):
        CreateFeatureRequest(
            feature_name="   ",
            feature_type="batch",
            feature_data_type="float",
            query="SELECT 1",
            description="desc",
            created_by="dev",
            user_role="developer",
        )


# Created by validator
def test_create_feature_request_created_by_validator():
    with pytest.raises(ValidationError):
        CreateFeatureRequest(
            feature_name="driver:hourly_stats:v1",
            feature_type="batch",
            feature_data_type="float",
            query="SELECT 1",
            description="desc",
            created_by=None,
            user_role="developer",
        )
    with pytest.raises(ValidationError):
        CreateFeatureRequest(
            feature_name="driver:hourly_stats:v1",
            feature_type="batch",
            feature_data_type="float",
            query="SELECT 1",
            description="desc",
            created_by="   ",
            user_role="developer",
        )


# Description validator
def test_create_feature_request_description_validator():
    with pytest.raises(ValidationError):
        CreateFeatureRequest(
            feature_name="driver:hourly_stats:v1",
            feature_type="batch",
            feature_data_type="float",
            query="SELECT 1",
            description=None,
            created_by="dev",
            user_role="developer",
        )
    with pytest.raises(ValidationError):
        CreateFeatureRequest(
            feature_name="driver:hourly_stats:v1",
            feature_type="batch",
            feature_data_type="float",
            query="SELECT 1",
            description="   ",
            created_by="dev",
            user_role="developer",
        )


# Query validator
def test_create_feature_request_query_validator():
    with pytest.raises(ValidationError):
        CreateFeatureRequest(
            feature_name="driver:hourly_stats:v1",
            feature_type="batch",
            feature_data_type="float",
            query=None,
            description="desc",
            created_by="dev",
            user_role="developer",
        )
    with pytest.raises(ValidationError):
        CreateFeatureRequest(
            feature_name="driver:hourly_stats:v1",
            feature_type="batch",
            feature_data_type="float",
            query="   ",
            description="desc",
            created_by="dev",
            user_role="developer",
        )


# User role validator
def test_get_feature_request_user_role_validator():
    with pytest.raises(ValidationError):
        GetFeatureRequest(feature_name="driver:hourly_stats:v1", user_role=None)
    with pytest.raises(ValidationError):
        GetFeatureRequest(feature_name="driver:hourly_stats:v1", user_role="   ")
