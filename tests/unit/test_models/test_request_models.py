import pytest
from pydantic import ValidationError

from app.models.request import (
    ApproveFeatureMetadataRequest,
    CreateFeatureMetadataRequest,
    DeleteFeatureMetadataRequest,
    FeatureMetadata,
    GetFeatureMetadataRequest,
    RejectFeatureMetadataRequest,
    SubmitTestFeatureMetadataRequest,
    TestFeatureMetadataRequest,
    UpdateFeatureMetadataRequest,
)


class TestFeatureMetadataModel:
    def test_valid(self):
        obj = FeatureMetadata(
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
        assert obj.feature_name == "test:feature:v1"

    def test_optional_fields(self):
        obj = FeatureMetadata(
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
            submitted_by=None,
            tested_by=None,
            tested_time=None,
            test_result=None,
            test_notes=None,
            approved_by=None,
            approved_time=None,
            approval_notes=None,
            rejected_by=None,
            rejection_reason=None,
            deployed_by=None,
            deployed_time=None,
            deleted_by=None,
            deleted_time=None,
            deletion_reason=None,
        )
        assert obj.last_updated_by is None


class TestGetFeatureMetadataRequest:
    def test_valid_str(self):
        req = GetFeatureMetadataRequest(
            features="test:feature:v1", user_role="developer"
        )
        assert req.features == "test:feature:v1"

    def test_valid_list(self):
        req = GetFeatureMetadataRequest(
            features=["test:feature:v1"], user_role="developer"
        )
        assert isinstance(req.features, list)

    def test_invalid_none(self):
        with pytest.raises(ValidationError):
            GetFeatureMetadataRequest(features=None, user_role="developer")

    def test_invalid_empty_str(self):
        with pytest.raises(ValidationError):
            GetFeatureMetadataRequest(features="", user_role="developer")

    def test_invalid_empty_list(self):
        with pytest.raises(ValidationError):
            GetFeatureMetadataRequest(features=[], user_role="developer")

    def test_invalid_list_with_empty(self):
        with pytest.raises(ValidationError):
            GetFeatureMetadataRequest(features=[""], user_role="developer")

    def test_invalid_user_role(self):
        with pytest.raises(ValidationError):
            GetFeatureMetadataRequest(features="test:feature:v1", user_role="")


class TestCreateFeatureMetadataRequest:
    def test_valid(self):
        req = CreateFeatureMetadataRequest(
            feature_name="test:feature:v1",
            feature_type="batch",
            feature_data_type="float",
            query="SELECT 1",
            description="desc",
            created_by="dev",
            user_role="developer",
        )
        assert req.feature_name == "test:feature:v1"

    def test_missing(self):
        with pytest.raises(ValidationError):
            CreateFeatureMetadataRequest(feature_name="test:feature:v1")


class TestUpdateFeatureMetadataRequest:
    def test_partial(self):
        req = UpdateFeatureMetadataRequest(
            feature_name="test:feature:v1",
            last_updated_by="dev",
            user_role="developer",
        )
        assert req.feature_name == "test:feature:v1"

    def test_all_fields(self):
        req = UpdateFeatureMetadataRequest(
            feature_name="test:feature:v1",
            feature_type="batch",
            feature_data_type="float",
            query="SELECT 1",
            description="desc",
            last_updated_by="dev",
            user_role="developer",
        )
        assert req.feature_type == "batch"


class TestDeleteFeatureMetadataRequest:
    def test_valid(self):
        req = DeleteFeatureMetadataRequest(
            feature_name="test:feature:v1",
            deleted_by="dev",
            user_role="developer",
            deletion_reason="reason",
        )
        assert req.deletion_reason == "reason"

    def test_missing_reason(self):
        with pytest.raises(ValidationError):
            DeleteFeatureMetadataRequest(
                feature_name="test:feature:v1",
                deleted_by="dev",
                user_role="developer",
            )


class TestSubmitTestFeatureMetadataRequest:
    def test_valid(self):
        req = SubmitTestFeatureMetadataRequest(
            feature_name="test:feature:v1",
            submitted_by="dev",
            user_role="developer",
        )
        assert req.submitted_by == "dev"


class TestTestFeatureMetadataRequest:
    def test_valid(self):
        req = TestFeatureMetadataRequest(
            feature_name="test:feature:v1",
            test_result="TEST_SUCCEEDED",
            tested_by="tester",
            user_role="tester",
        )
        assert req.test_result == "TEST_SUCCEEDED"

    def test_optional_notes(self):
        req = TestFeatureMetadataRequest(
            feature_name="test:feature:v1",
            test_result="TEST_FAILED",
            tested_by="tester",
            user_role="tester",
            test_notes="fail",
        )
        assert req.test_notes == "fail"


class TestApproveFeatureMetadataRequest:
    def test_valid(self):
        req = ApproveFeatureMetadataRequest(
            feature_name="test:feature:v1",
            approved_by="approver",
            user_role="approver",
        )
        assert req.approved_by == "approver"

    def test_optional_notes(self):
        req = ApproveFeatureMetadataRequest(
            feature_name="test:feature:v1",
            approved_by="approver",
            user_role="approver",
            approval_notes="ok",
        )
        assert req.approval_notes == "ok"


class TestRejectFeatureMetadataRequest:
    def test_valid(self):
        req = RejectFeatureMetadataRequest(
            feature_name="test:feature:v1",
            rejected_by="approver",
            rejection_reason="reason",
            user_role="approver",
        )
        assert req.rejection_reason == "reason"
