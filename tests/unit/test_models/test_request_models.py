"""Test request model validation."""

import pytest
from pydantic import ValidationError

from app.models.request import (
    ApproveFeatureRequest,
    CreateFeatureRequest,
    GetAllFeaturesRequest,
    GetFeatureRequest,
    RejectFeatureRequest,
    TestFeatureRequest,
    UpdateFeatureRequest,
    DeleteFeatureRequest,
    ReadyTestRequest,
    ReadyTestFeatureRequest,
    FixFeatureRequest,
    BatchFeatureResult,
    BatchFeatureRequest,
    BatchFeatureResponse,
    FeatureMetadata,
)


class TestCreateFeatureRequest:
    def test_valid_request(self):
        req = CreateFeatureRequest(
            feature_name="driver:hourly_stats:v1",
            feature_type="real-time",
            feature_data_type="float",
            query="SELECT conv_rate FROM driver_hourly_stats WHERE driver_id = ?",
            description="Conversion rate for driver",
            created_by="Fia",
            user_role="developer"
        )
        assert req.feature_name == "driver:hourly_stats:v1"

    def test_missing_required_fields(self):
        with pytest.raises(ValidationError):
            CreateFeatureRequest(
                feature_name="driver:hourly_stats:v1"
            )

    def test_empty_string_validation(self):
        with pytest.raises(ValidationError):
            CreateFeatureRequest(
                feature_name="",
                feature_type="real-time",
                feature_data_type="float",
                query="SELECT conv_rate FROM driver_hourly_stats WHERE driver_id = ?",
                description="Conversion rate for driver",
                created_by="Fia",
                user_role="developer"
            )

    def test_feature_name_validation(self):
        valid_names = [
            "driver:hourly_stats:v1",
            "fraud:amount:v1",
            "customer:income:v2"
        ]
        for name in valid_names:
            req = CreateFeatureRequest(
                feature_name=name,
                feature_type="real-time",
                feature_data_type="float",
                query="SELECT 1",
                description="desc",
                created_by="dev",
                user_role="developer"
            )
            assert req.feature_name == name

    def test_created_by_validation(self):
        with pytest.raises(ValidationError):
            CreateFeatureRequest(
                feature_name="driver:hourly_stats:v1",
                feature_type="real-time",
                feature_data_type="float",
                query="SELECT 1",
                description="desc",
                created_by="",
                user_role="developer"
            )

    def test_description_validation(self):
        with pytest.raises(ValidationError):
            CreateFeatureRequest(
                feature_name="driver:hourly_stats:v1",
                feature_type="real-time",
                feature_data_type="float",
                query="SELECT 1",
                description="",
                created_by="dev",
                user_role="developer"
            )

    def test_query_validation(self):
        with pytest.raises(ValidationError):
            CreateFeatureRequest(
                feature_name="driver:hourly_stats:v1",
                feature_type="real-time",
                feature_data_type="float",
                query="",
                description="desc",
                created_by="dev",
                user_role="developer"
            )

class TestUpdateFeatureRequest:
    def test_partial_update(self):
        req = UpdateFeatureRequest(
            feature_name="driver:hourly_stats:v1",
            description="Updated desc",
            last_updated_by="Fia",
            user_role="developer"
        )
        assert req.description == "Updated desc"
        assert req.feature_type is None

    def test_all_fields_update(self):
        req = UpdateFeatureRequest(
            feature_name="driver:hourly_stats:v1",
            feature_type="real-time",
            feature_data_type="float",
            query="SELECT conv_rate FROM driver_hourly_stats WHERE driver_id = ?",
            description="desc",
            status="READY_FOR_TESTING",
            last_updated_by="Fia",
            user_role="developer"
        )
        assert req.feature_type == "real-time"
        assert req.status == "READY_FOR_TESTING"

    def test_optional_fields(self):
        req = UpdateFeatureRequest(
            feature_name="driver:hourly_stats:v1",
            last_updated_by="Fia",
            user_role="developer"
        )
        assert req.feature_type is None
        assert req.feature_data_type is None
        assert req.query is None

class TestTestFeatureRequest:
    def test_valid_test_success(self):
        req = TestFeatureRequest(
            feature_name="driver:hourly_stats:v1",
            test_result="TEST_SUCCEEDED",
            tested_by="test_system",
            user_role="external_testing_system",
            test_notes="All tests passed"
        )
        assert req.test_result == "TEST_SUCCEEDED"

    def test_valid_test_failure(self):
        req = TestFeatureRequest(
            feature_name="driver:hourly_stats:v1",
            test_result="TEST_FAILED",
            tested_by="test_system",
            user_role="external_testing_system",
            test_notes="Validation failed"
        )
        assert req.test_result == "TEST_FAILED"

    def test_optional_notes(self):
        req = TestFeatureRequest(
            feature_name="driver:hourly_stats:v1",
            test_result="TEST_SUCCEEDED",
            tested_by="test_system",
            user_role="external_testing_system"
        )
        assert req.test_notes is None

class TestApproveRejectRequests:
    def test_approve_request(self):
        req = ApproveFeatureRequest(
            feature_name="driver:hourly_stats:v1",
            approved_by="Endy",
            user_role="approver",
            approval_notes="Approved"
        )
        assert req.approved_by == "Endy"
        assert req.approval_notes == "Approved"

    def test_reject_request(self):
        req = RejectFeatureRequest(
            feature_name="driver:hourly_stats:v1",
            rejected_by="Endy",
            user_role="approver",
            rejection_reason="Not valid"
        )
        assert req.rejected_by == "Endy"
        assert req.rejection_reason == "Not valid"

class TestGetRequests:
    def test_get_metadata_request(self):
        req = GetFeatureRequest(
            feature_name="driver:hourly_stats:v1",
            user_role="developer"
        )
        assert req.feature_name == "driver:hourly_stats:v1"
        assert req.user_role == "developer"
        with pytest.raises(ValidationError):
            GetFeatureRequest(user_role="developer")
        with pytest.raises(ValidationError):
            GetFeatureRequest(feature_name="", user_role="developer")
        with pytest.raises(ValidationError):
            GetFeatureRequest(feature_name="invalid", user_role="developer")

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
            user_role="developer"
        )
        assert req.status == "DEPLOYED"
        assert req.feature_type == "batch"
        assert req.created_by == "Ludy"
        assert req.limit == 10
        assert req.offset == 5
        assert req.user_role == "developer"

class TestDeleteReadyFixRequests:
    def test_delete_feature_request(self):
        req = DeleteFeatureRequest(
            feature_name="driver:hourly_stats:v1",
            deleted_by="dev",
            deletion_reason="Cleanup",
            user_role="developer"
        )
        assert req.deletion_reason == "Cleanup"

    def test_ready_test_request(self):
        req = ReadyTestRequest(
            feature_name="driver:hourly_stats:v1",
            submitted_by="dev",
            user_role="developer"
        )
        assert req.submitted_by == "dev"

    def test_ready_test_feature_request(self):
        req = ReadyTestFeatureRequest(
            feature_name="driver:hourly_stats:v1",
            submitted_by="dev",
            user_role="developer"
        )
        assert req.submitted_by == "dev"

    def test_fix_feature_request(self):
        req = FixFeatureRequest(
            feature_name="driver:hourly_stats:v1",
            fixed_by="dev",
            fix_description="Fixed bug",
            user_role="developer"
        )
        assert req.fix_description == "Fixed bug"

class TestBatchFeatureResultRequest:
    def test_batch_feature_result(self):
        result = BatchFeatureResult(
            values=[1, 2, 3],
            messages=["ok", "ok", "ok"],
            event_timestamps=[1, 2, 3]
        )
        assert result.values == [1, 2, 3]

    def test_batch_feature_request(self):
        req = BatchFeatureRequest(
            features=["driver:hourly_stats:v1"],
            entities={"driver_id": ["D123"]},
            event_timestamp=1640995200000
        )
        assert req.features == ["driver:hourly_stats:v1"]
        assert req.entities["driver_id"] == ["D123"]

    def test_batch_feature_response(self):
        result = BatchFeatureResult(
            values=[1, 2, 3],
            messages=["ok", "ok", "ok"],
            event_timestamps=[1, 2, 3]
        )
        resp = BatchFeatureResponse(
            metadata={"driver:hourly_stats:v1": {}},
            results=[result]
        )
        assert isinstance(resp.results, list)

class TestFeatureMetadataModel:
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
            created_by="dev"
        )
        assert meta.feature_name == "driver:hourly_stats:v1"
        assert meta.status == "DRAFT"

def test_create_feature_request_feature_name_validator():
    # Line 58: not a string or empty
    with pytest.raises(Exception):
        CreateFeatureRequest(
            feature_name=None,
            feature_type="batch",
            feature_data_type="float",
            query="SELECT 1",
            description="desc",
            created_by="dev",
            user_role="developer"
        )
    with pytest.raises(Exception):
        CreateFeatureRequest(
            feature_name="   ",
            feature_type="batch",
            feature_data_type="float",
            query="SELECT 1",
            description="desc",
            created_by="dev",
            user_role="developer"
        )

def test_create_feature_request_created_by_validator():
    # Line 83: not a string or empty
    with pytest.raises(Exception):
        CreateFeatureRequest(
            feature_name="driver:hourly_stats:v1",
            feature_type="batch",
            feature_data_type="float",
            query="SELECT 1",
            description="desc",
            created_by=None,
            user_role="developer"
        )
    with pytest.raises(Exception):
        CreateFeatureRequest(
            feature_name="driver:hourly_stats:v1",
            feature_type="batch",
            feature_data_type="float",
            query="SELECT 1",
            description="desc",
            created_by="   ",
            user_role="developer"
        )

def test_create_feature_request_description_validator():
    # Line 89: not a string or empty
    with pytest.raises(Exception):
        CreateFeatureRequest(
            feature_name="driver:hourly_stats:v1",
            feature_type="batch",
            feature_data_type="float",
            query="SELECT 1",
            description=None,
            created_by="dev",
            user_role="developer"
        )
    with pytest.raises(Exception):
        CreateFeatureRequest(
            feature_name="driver:hourly_stats:v1",
            feature_type="batch",
            feature_data_type="float",
            query="SELECT 1",
            description="   ",
            created_by="dev",
            user_role="developer"
        )

def test_create_feature_request_query_validator():
    # Line 95: not a string or empty
    with pytest.raises(Exception):
        CreateFeatureRequest(
            feature_name="driver:hourly_stats:v1",
            feature_type="batch",
            feature_data_type="float",
            query=None,
            description="desc",
            created_by="dev",
            user_role="developer"
        )
    with pytest.raises(Exception):
        CreateFeatureRequest(
            feature_name="driver:hourly_stats:v1",
            feature_type="batch",
            feature_data_type="float",
            query="   ",
            description="desc",
            created_by="dev",
            user_role="developer"
        )
        
def test_get_feature_request_user_role_validator():
    # Covers line 58: user_role is empty or not a string
    with pytest.raises(Exception):
        GetFeatureRequest(feature_name="driver:hourly_stats:v1", user_role=None)
    with pytest.raises(Exception):
        GetFeatureRequest(feature_name="driver:hourly_stats:v1", user_role="   ")