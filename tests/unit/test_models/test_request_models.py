# """Test request model validation."""

# import pytest
# from pydantic import ValidationError

# from app.models.request import (
#     ApproveFeatureRequest,
#     CreateFeatureRequest,
#     GetAllFeaturesRequest,
#     GetFeatureRequest,
#     RejectFeatureRequest,
#     TestFeatureRequest,
#     UpdateFeatureRequest,
# )


# class TestCreateFeatureRequest:
#     """Test create feature request model."""

#     def test_valid_request(self):
#         """Valid create request."""
#         req = CreateFeatureRequest(
#             feature_name="driver_hourly_stats:conv_rate:1",
#             feature_type="real-time",
#             feature_data_type="float",
#             query="SELECT conv_rate FROM driver_hourly_stats WHERE driver_id = ?",
#             description="Conversion rate for driver",
#             created_by="Fia",
#             user_role="developer"
#         )
#         assert req.feature_name == "driver_hourly_stats:conv_rate:1"
#         assert req.feature_type == "real-time"

#     def test_missing_required_fields(self):
#         """Missing required fields."""
#         with pytest.raises(ValidationError):
#             CreateFeatureRequest(
#                 feature_name="driver_hourly_stats:conv_rate:1"
#                 # Missing other required fields
#             )

#     def test_empty_string_validation(self):
#         """Empty string validation."""
#         with pytest.raises(ValidationError):
#             CreateFeatureRequest(
#                 feature_name="",
#                 feature_type="real-time",
#                 feature_data_type="float",
#                 query="SELECT conv_rate FROM driver_hourly_stats WHERE driver_id = ?",
#                 description="Conversion rate for driver",
#                 created_by="Fia",
#                 user_role="developer"
#             )

#     def test_feature_name_validation(self):
#         """Feature name format validation."""
#         valid_names = [
#             "driver_hourly_stats:conv_rate:1",
#             "fraud:amount:v1",
#             "customer:income:v2"
#         ]
#         for name in valid_names:
#             req = CreateFeatureRequest(
#                 feature_name=name,
#                 feature_type="real-time",
#                 feature_data_type="float",
#                 query="SELECT 1",
#                 description="desc",
#                 created_by="dev",
#                 user_role="developer"
#             )
#             assert req.feature_name == name

#     def test_created_by_validation(self):
#         """created_by validation."""
#         with pytest.raises(ValidationError):
#             CreateFeatureRequest(
#                 feature_name="driver_hourly_stats:conv_rate:1",
#                 feature_type="real-time",
#                 feature_data_type="float",
#                 query="SELECT 1",
#                 description="desc",
#                 created_by="",
#                 user_role="developer"
#             )

# class TestUpdateFeatureRequest:
#     """Test update feature request model."""

#     def test_partial_update(self):
#         """Partial update."""
#         req = UpdateFeatureRequest(
#             feature_name="driver_hourly_stats:conv_rate:1",
#             description="Updated desc",
#             last_updated_by="Fia",
#             user_role="developer"
#         )
#         assert req.description == "Updated desc"
#         assert req.feature_type is None

#     def test_all_fields_update(self):
#         """All fields update."""
#         req = UpdateFeatureRequest(
#             feature_name="driver_hourly_stats:conv_rate:1",
#             feature_type="real-time",
#             feature_data_type="float",
#             query="SELECT conv_rate FROM driver_hourly_stats WHERE driver_id = ?",
#             description="desc",
#             status="READY_FOR_TESTING",
#             last_updated_by="Fia",
#             user_role="developer"
#         )
#         assert req.feature_type == "real-time"
#         assert req.status == "READY_FOR_TESTING"

#     def test_optional_fields(self):
#         """Optional fields."""
#         req = UpdateFeatureRequest(
#             feature_name="driver_hourly_stats:conv_rate:1",
#             last_updated_by="Fia",
#             user_role="developer"
#         )
#         assert req.feature_type is None
#         assert req.feature_data_type is None
#         assert req.query is None

# class TestTestFeatureRequest:
#     """Test feature testing request model."""

#     def test_valid_test_success(self):
#         """Valid test success."""
#         req = TestFeatureRequest(
#             feature_name="driver_hourly_stats:conv_rate:1",
#             test_result="TEST_SUCCEEDED",
#             tested_by="test_system",
#             user_role="external_testing_system",
#             test_notes="All tests passed"
#         )
#         assert req.test_result == "TEST_SUCCEEDED"

#     def test_valid_test_failure(self):
#         """Valid test failure."""
#         req = TestFeatureRequest(
#             feature_name="driver_hourly_stats:conv_rate:1",
#             test_result="TEST_FAILED",
#             tested_by="test_system",
#             user_role="external_testing_system",
#             test_notes="Validation failed"
#         )
#         assert req.test_result == "TEST_FAILED"

#     def test_optional_notes(self):
#         """Optional test notes."""
#         req = TestFeatureRequest(
#             feature_name="driver_hourly_stats:conv_rate:1",
#             test_result="TEST_SUCCEEDED",
#             tested_by="test_system",
#             user_role="external_testing_system"
#         )
#         assert req.test_notes is None

# class TestApproveRejectRequests:
#     """Test approve and reject request models."""

#     def test_approve_request(self):
#         """Approve request."""
#         req = ApproveFeatureRequest(
#             feature_name="driver_hourly_stats:conv_rate:1",
#             approved_by="Endy",
#             user_role="approver",
#             approval_notes="Approved"
#         )
#         assert req.approved_by == "Endy"
#         assert req.approval_notes == "Approved"

#     def test_reject_request(self):
#         """Reject request."""
#         req = RejectFeatureRequest(
#             feature_name="driver_hourly_stats:conv_rate:1",
#             rejected_by="Endy",
#             user_role="approver",
#             rejection_reason="Not valid"
#         )
#         assert req.rejected_by == "Endy"
#         assert req.rejection_reason == "Not valid"

# class TestGetRequests:
#     """Test get request models."""

#     def test_get_metadata_request(self):
#         """Get metadata request."""
#         # Use a valid feature name format for your regex
#         req = GetFeatureRequest(
#             feature_name="driver:hourly_stats:conv_rate:v1",
#             user_role="developer"
#         )
#         assert req.feature_name == "driver:hourly_stats:conv_rate:v1"
#         assert req.user_role == "developer"
#         with pytest.raises(ValidationError):
#             GetFeatureRequest(user_role="developer")

#     def test_get_all_features_request(self):
#         """Get all features request."""
#         req = GetAllFeaturesRequest(user_role="developer")
#         assert req.status is None
#         assert req.feature_type is None
#         assert req.created_by is None
#         assert req.limit is None
#         assert req.offset is None
#         assert req.user_role == "developer"
#         req = GetAllFeaturesRequest(
#             status="DEPLOYED",
#             feature_type="batch",
#             created_by="Ludy",
#             limit=10,
#             offset=5,
#             user_role="developer"
#         )
#         assert req.status == "DEPLOYED"
#         assert req.feature_type == "batch"
#         assert req.created_by == "Ludy"
#         assert req.limit == 10
#         assert req.offset == 5
#         assert req.user_role == "developer"
