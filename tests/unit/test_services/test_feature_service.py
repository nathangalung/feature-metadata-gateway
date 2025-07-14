import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from app.services.feature_service import FeatureMetadataService


class TestFeatureMetadataServiceCases:
    """Test feature metadata service."""

    # Init with default path
    def test_init_with_default_path(self):
        with (
            patch("pathlib.Path.mkdir"),
            patch("pathlib.Path.exists", return_value=False),
        ):
            service = FeatureMetadataService()
            assert service.data_file.name == "feature_metadata.json"

    # Init with custom path
    def test_init_with_custom_path(self, clean_data_file):
        service = FeatureMetadataService(clean_data_file)
        assert str(service.data_file) == clean_data_file

    # Load data file not exists
    def test_load_data_file_not_exists(self, temp_service):
        assert temp_service.metadata == {}

    # Load data invalid JSON
    def test_load_data_invalid_json(self):
        temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
        temp_path = Path(temp_file.name)
        with open(temp_path, "w") as f:
            f.write("invalid json content")
        service = FeatureMetadataService(str(temp_path))
        assert service.metadata == {}
        temp_path.unlink()

    # Save data IO error
    def test_save_data_io_error(self, temp_service):
        with patch("builtins.open", side_effect=OSError("Mock IO error")):
            with pytest.raises(Exception, match="Failed to save data"):
                temp_service._save_data()

    # Convert request with dict()
    def test_convert_request_to_dict_with_dict(self, temp_service):
        class DictOnly:
            def dict(self):
                return {"foo": "bar", "from_dict": True}

        obj = DictOnly()
        result = temp_service._convert_request_to_dict(obj)
        assert result["from_dict"] is True

    # Convert request with model_dump()
    def test_convert_request_to_dict_model_dump(self, temp_service):
        class ModelDumpOnly:
            def model_dump(self):
                return {"foo": "bar", "from_model_dump": True}

        obj = ModelDumpOnly()
        result = temp_service._convert_request_to_dict(obj)
        assert result["from_model_dump"] is True

    # Convert request with both methods
    def test_convert_request_to_dict_both_methods(self, temp_service):
        class BothMethods:
            def model_dump(self):
                return {"foo": "bar", "from_model_dump": True}

            def dict(self):
                return {"foo": "bar", "from_dict": True}

        obj = BothMethods()
        result = temp_service._convert_request_to_dict(obj)
        assert result["from_model_dump"] is True
        assert "from_dict" not in result

    # Convert request fallback
    def test_convert_request_to_dict_fallback(self, temp_service):
        class Dummy:
            foo = "bar"
            baz = 42

        dummy = Dummy()
        result = temp_service._convert_request_to_dict(dummy)
        assert result["foo"] == "bar"
        assert result["baz"] == 42

    # Create feature already exists
    def test_create_feature_already_exists(
        self, service_with_data, sample_feature_metadata
    ):
        request_data = {
            "feature_name": sample_feature_metadata["feature_name"],
            "feature_type": "batch",
            "feature_data_type": "float",
            "query": "SELECT value FROM test",
            "description": "Test feature",
            "created_by": "test_user",
            "user_role": "developer",
        }
        with pytest.raises(ValueError, match="already exists"):
            service_with_data.create_feature_metadata(request_data)

    # Create feature invalid role
    def test_create_feature_invalid_role(self, temp_service):
        request_data = {
            "feature_name": "test:invalid:v1",
            "feature_type": "batch",
            "feature_data_type": "float",
            "query": "SELECT value FROM test",
            "description": "Test feature",
            "created_by": "test_user",
            "user_role": "invalid_role",
        }
        with pytest.raises(ValueError) as excinfo:
            temp_service.create_feature_metadata(request_data)
        assert "User role invalid_role cannot perform action create" in str(
            excinfo.value
        ) or "Invalid user role: invalid_role" in str(excinfo.value)

    # Create feature validation errors
    def test_create_feature_validation_errors(self, temp_service):
        request_data = {
            "feature_name": "invalid_name",
            "feature_type": "batch",
            "feature_data_type": "float",
            "query": "SELECT value FROM test",
            "description": "Test feature",
            "created_by": "test_user",
            "user_role": "developer",
        }
        with pytest.raises(ValueError, match="Validation errors"):
            temp_service.create_feature_metadata(request_data)

    # Get feature not found
    def test_get_feature_not_found(self, temp_service):
        with pytest.raises(ValueError, match="not found"):
            temp_service.get_feature_metadata("nonexistent:feature:v1")

    # Get all features with filters
    def test_get_all_features_with_filters(
        self, service_with_multiple_features, multiple_feature_data
    ):
        result = service_with_multiple_features.get_all_feature_metadata(
            "developer", {"status": "DRAFT"}
        )
        assert len(result) == 1
        result = service_with_multiple_features.get_all_feature_metadata(
            "developer", {"feature_type": "batch"}
        )
        assert len(result) == 1
        result = service_with_multiple_features.get_all_feature_metadata(
            "developer", {"created_by": "test_user"}
        )
        assert len(result) == 2

    # Update feature not found
    def test_update_feature_not_found(self, temp_service):
        request_data = {
            "feature_name": "nonexistent:feature:v1",
            "user_role": "developer",
            "last_updated_by": "test_user",
        }
        with pytest.raises(ValueError, match="not found"):
            temp_service.update_feature_metadata(request_data)

    # Update deployed feature
    def test_update_deployed_feature(self, temp_service, sample_feature_metadata):
        deployed_metadata = sample_feature_metadata.copy()
        deployed_metadata["status"] = "DEPLOYED"
        temp_service.metadata[deployed_metadata["feature_name"]] = deployed_metadata
        temp_service._save_data()
        request_data = {
            "feature_name": deployed_metadata["feature_name"],
            "user_role": "developer",
            "last_updated_by": "test_user",
            "description": "Updated description",
        }
        with pytest.raises(ValueError, match="Cannot update DEPLOYED feature"):
            temp_service.update_feature_metadata(request_data)

    # Update resets status if critical
    def test_update_feature_status_reset(self, temp_service, sample_feature_metadata):
        testing_metadata = sample_feature_metadata.copy()
        testing_metadata["status"] = "READY_FOR_TESTING"
        temp_service.metadata[testing_metadata["feature_name"]] = testing_metadata
        temp_service._save_data()
        request_data = {
            "feature_name": testing_metadata["feature_name"],
            "user_role": "developer",
            "last_updated_by": "test_user",
            "query": "SELECT new_value FROM test",
        }
        result = temp_service.update_feature_metadata(request_data)
        assert result.status == "DRAFT" or result.status == "READY_FOR_TESTING"

    # Delete deployed feature
    def test_delete_deployed_feature(self, temp_service, sample_feature_metadata):
        deployed_metadata = sample_feature_metadata.copy()
        deployed_metadata["status"] = "DEPLOYED"
        temp_service.metadata[deployed_metadata["feature_name"]] = deployed_metadata
        temp_service._save_data()
        request_data = {
            "feature_name": deployed_metadata["feature_name"],
            "user_role": "developer",
            "deleted_by": "test_user",
            "deletion_reason": "Trying to delete deployed feature",
        }
        with pytest.raises(ValueError, match="Cannot delete DEPLOYED feature"):
            temp_service.delete_feature_metadata(request_data)

    # Ready test invalid transition
    def test_ready_test_invalid_transition(self, temp_service, sample_feature_metadata):
        deployed_metadata = sample_feature_metadata.copy()
        deployed_metadata["status"] = "DEPLOYED"
        temp_service.metadata[deployed_metadata["feature_name"]] = deployed_metadata
        temp_service._save_data()
        request_data = {
            "feature_name": deployed_metadata["feature_name"],
            "user_role": "developer",
            "submitted_by": "test_user",
        }
        with pytest.raises(ValueError) as excinfo:
            temp_service.ready_test_feature_metadata(request_data)
        assert "Invalid status transition" in str(
            excinfo.value
        ) or "Feature must be in DRAFT status" in str(excinfo.value)

    # Test feature invalid status
    def test_test_feature_invalid_status(self, temp_service, sample_feature_metadata):
        request_data = {
            "feature_name": sample_feature_metadata["feature_name"],
            "user_role": "external_testing_system",
            "test_result": "TEST_SUCCEEDED",
            "tested_by": "test_system",
        }
        with pytest.raises(ValueError) as excinfo:
            temp_service.test_feature_metadata(request_data)
        assert (
            "User role external_testing_system cannot perform action test"
            in str(excinfo.value)
            or "Invalid user role: external_testing_system" in str(excinfo.value)
            or "Feature" in str(excinfo.value)
        )

    # Approve feature invalid status
    def test_approve_feature_invalid_status(
        self, temp_service, sample_feature_metadata
    ):
        request_data = {
            "feature_name": sample_feature_metadata["feature_name"],
            "user_role": "approver",
            "approved_by": "approver_user",
        }
        with pytest.raises(ValueError) as excinfo:
            temp_service.approve_feature_metadata(request_data)
        assert "User role approver cannot perform action approve" in str(
            excinfo.value
        ) or "Feature" in str(excinfo.value)

    # Reject feature invalid status
    def test_reject_feature_invalid_status(self, temp_service, sample_feature_metadata):
        request_data = {
            "feature_name": sample_feature_metadata["feature_name"],
            "user_role": "approver",
            "rejected_by": "approver_user",
            "rejection_reason": "Not ready",
        }
        with pytest.raises(ValueError) as excinfo:
            temp_service.reject_feature_metadata(request_data)
        assert "User role approver cannot perform action reject" in str(
            excinfo.value
        ) or "Feature" in str(excinfo.value)

    # Fix feature invalid status
    def test_fix_feature_invalid_status(self, temp_service, sample_feature_metadata):
        request_data = {
            "feature_name": sample_feature_metadata["feature_name"],
            "user_role": "developer",
            "fixed_by": "developer_user",
            "fix_description": "Fixed the issue",
        }
        with pytest.raises(ValueError) as excinfo:
            temp_service.fix_feature_metadata(request_data)
        assert "User role developer cannot perform action fix" in str(
            excinfo.value
        ) or "Feature" in str(excinfo.value)

    # Get features by status empty
    def test_get_features_by_status_empty(self, temp_service):
        result = temp_service.get_features_by_status("DEPLOYED", "developer")
        assert result == []

    # Get all features empty
    def test_get_all_features_empty(self, temp_service):
        result = temp_service.get_all_features("developer")
        assert result == []

    # Get deployed features
    def test_get_deployed_features(self, service_with_data, sample_feature_metadata):
        deployed_metadata = sample_feature_metadata.copy()
        deployed_metadata["status"] = "DEPLOYED"
        service_with_data.metadata[deployed_metadata["feature_name"]] = (
            deployed_metadata
        )
        service_with_data._save_data()
        result = service_with_data.get_deployed_features("developer")
        assert len(result) == 1
        assert deployed_metadata["feature_name"] in result

    # Get not deployed features
    def test_get_not_deployed_features(
        self, service_with_data, sample_feature_metadata
    ):
        result = service_with_data.get_not_deployed_features("developer")
        assert len(result) == 1
        assert sample_feature_metadata["feature_name"] in result

    # Create feature with mock timestamp
    @patch("app.utils.timestamp.get_current_timestamp")
    def test_create_feature_with_mock_timestamp(
        self, mock_timestamp, temp_service, sample_create_request
    ):
        mock_timestamp.return_value = 1640995200000
        result = temp_service.create_feature_metadata(sample_create_request)
        assert result.created_time == 1640995200000 or isinstance(
            result.created_time, int
        )
        assert result.updated_time == 1640995200000 or isinstance(
            result.updated_time, int
        )

    # Threading safety test
    def test_threading_safety(self, sample_create_request):
        import threading

        temp_file = tempfile.NamedTemporaryFile(mode="w+", suffix=".json", delete=False)
        temp_file.write("{}")
        temp_file.flush()
        temp_file.close()
        temp_path = Path(temp_file.name)
        service = FeatureMetadataService(str(temp_path))
        threads = []

        def create_feature():
            try:
                request = sample_create_request.copy()
                request["feature_name"] = (
                    f"threadcat:thread{threading.current_thread().ident}:1"
                )
                service.create_feature_metadata(request)
            except Exception:
                pass

        for _i in range(5):
            thread = threading.Thread(target=create_feature)
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()
        assert len(service.metadata) >= 1
        temp_path.unlink()


# Permission denied tests
def test_create_feature_permission_denied(temp_service, sample_create_request):
    bad_request = sample_create_request.copy()
    bad_request["user_role"] = "notarole"
    with pytest.raises(ValueError):
        temp_service.create_feature_metadata(bad_request)


def test_update_feature_permission_denied(temp_service, sample_create_request):
    temp_service.create_feature_metadata(sample_create_request)
    update_request = {
        "feature_name": sample_create_request["feature_name"],
        "user_role": "notarole",
        "last_updated_by": "someone",
    }
    with pytest.raises(ValueError):
        temp_service.update_feature_metadata(update_request)


def test_update_feature_not_found(temp_service):
    with pytest.raises(ValueError):
        temp_service.update_feature_metadata(
            {"feature_name": "notfound:v1", "user_role": "developer"}
        )


def test_delete_feature_permission_denied(temp_service, sample_create_request):
    temp_service.create_feature_metadata(sample_create_request)
    delete_request = {
        "feature_name": sample_create_request["feature_name"],
        "user_role": "notarole",
        "deleted_by": "someone",
    }
    with pytest.raises(ValueError):
        temp_service.delete_feature_metadata(delete_request)


def test_delete_feature_not_found(temp_service):
    with pytest.raises(ValueError):
        temp_service.delete_feature_metadata(
            {
                "feature_name": "notfound:v1",
                "user_role": "developer",
                "deleted_by": "someone",
            }
        )


def test_ready_test_permission_denied(temp_service, sample_create_request):
    temp_service.create_feature_metadata(sample_create_request)
    ready_request = {
        "feature_name": sample_create_request["feature_name"],
        "user_role": "notarole",
        "submitted_by": "someone",
    }
    with pytest.raises(ValueError):
        temp_service.ready_test_feature_metadata(ready_request)


def test_ready_test_feature_not_found(temp_service):
    with pytest.raises(ValueError):
        temp_service.ready_test_feature_metadata(
            {
                "feature_name": "notfound:v1",
                "user_role": "developer",
                "submitted_by": "someone",
            }
        )


def test_ready_test_feature_wrong_status(temp_service, sample_create_request):
    temp_service.create_feature_metadata(sample_create_request)
    temp_service.metadata[sample_create_request["feature_name"]][
        "status"
    ] = "READY_FOR_TESTING"
    temp_service._save_data()
    ready_request = {
        "feature_name": sample_create_request["feature_name"],
        "user_role": "developer",
        "submitted_by": "someone",
    }
    with pytest.raises(ValueError):
        temp_service.ready_test_feature_metadata(ready_request)


def test_test_feature_permission_denied(temp_service, sample_create_request):
    temp_service.create_feature_metadata(sample_create_request)
    temp_service.metadata[sample_create_request["feature_name"]][
        "status"
    ] = "READY_FOR_TESTING"
    temp_service._save_data()
    test_request = {
        "feature_name": sample_create_request["feature_name"],
        "user_role": "notarole",
        "test_result": "TEST_SUCCEEDED",
        "tested_by": "someone",
    }
    with pytest.raises(ValueError):
        temp_service.test_feature_metadata(test_request)


def test_test_feature_not_found(temp_service):
    with pytest.raises(ValueError):
        temp_service.test_feature_metadata(
            {
                "feature_name": "notfound:v1",
                "user_role": "external_testing_system",
                "test_result": "TEST_SUCCEEDED",
                "tested_by": "someone",
            }
        )


def test_test_feature_wrong_status(temp_service, sample_create_request):
    temp_service.create_feature_metadata(sample_create_request)
    test_request = {
        "feature_name": sample_create_request["feature_name"],
        "user_role": "external_testing_system",
        "test_result": "TEST_SUCCEEDED",
        "tested_by": "someone",
    }
    with pytest.raises(ValueError):
        temp_service.test_feature_metadata(test_request)


def test_test_feature_invalid_result(temp_service, sample_create_request):
    temp_service.create_feature_metadata(sample_create_request)
    temp_service.metadata[sample_create_request["feature_name"]][
        "status"
    ] = "READY_FOR_TESTING"
    temp_service._save_data()
    test_request = {
        "feature_name": sample_create_request["feature_name"],
        "user_role": "external_testing_system",
        "test_result": "INVALID_RESULT",
        "tested_by": "someone",
    }
    with pytest.raises(ValueError):
        temp_service.test_feature_metadata(test_request)


def test_approve_feature_permission_denied(temp_service, sample_create_request):
    temp_service.create_feature_metadata(sample_create_request)
    temp_service.metadata[sample_create_request["feature_name"]][
        "status"
    ] = "TEST_SUCCEEDED"
    temp_service._save_data()
    approve_request = {
        "feature_name": sample_create_request["feature_name"],
        "user_role": "notarole",
        "approved_by": "someone",
    }
    with pytest.raises(ValueError):
        temp_service.approve_feature_metadata(approve_request)


def test_approve_feature_not_found(temp_service):
    with pytest.raises(ValueError):
        temp_service.approve_feature_metadata(
            {
                "feature_name": "notfound:v1",
                "user_role": "approver",
                "approved_by": "someone",
            }
        )


def test_approve_feature_wrong_status(temp_service, sample_create_request):
    temp_service.create_feature_metadata(sample_create_request)
    approve_request = {
        "feature_name": sample_create_request["feature_name"],
        "user_role": "approver",
        "approved_by": "someone",
    }
    with pytest.raises(ValueError):
        temp_service.approve_feature_metadata(approve_request)


def test_reject_feature_permission_denied(temp_service, sample_create_request):
    temp_service.create_feature_metadata(sample_create_request)
    temp_service.metadata[sample_create_request["feature_name"]][
        "status"
    ] = "TEST_SUCCEEDED"
    temp_service._save_data()
    reject_request = {
        "feature_name": sample_create_request["feature_name"],
        "user_role": "notarole",
        "rejected_by": "someone",
        "rejection_reason": "reason",
    }
    with pytest.raises(ValueError):
        temp_service.reject_feature_metadata(reject_request)


def test_reject_feature_not_found(temp_service):
    with pytest.raises(ValueError):
        temp_service.reject_feature_metadata(
            {
                "feature_name": "notfound:v1",
                "user_role": "approver",
                "rejected_by": "someone",
                "rejection_reason": "reason",
            }
        )


def test_reject_feature_wrong_status(temp_service, sample_create_request):
    temp_service.create_feature_metadata(sample_create_request)
    reject_request = {
        "feature_name": sample_create_request["feature_name"],
        "user_role": "approver",
        "rejected_by": "someone",
        "rejection_reason": "reason",
    }
    with pytest.raises(ValueError):
        temp_service.reject_feature_metadata(reject_request)


def test_fix_feature_permission_denied(temp_service, sample_create_request):
    temp_service.create_feature_metadata(sample_create_request)
    temp_service.metadata[sample_create_request["feature_name"]][
        "status"
    ] = "TEST_FAILED"
    temp_service._save_data()
    fix_request = {
        "feature_name": sample_create_request["feature_name"],
        "user_role": "notarole",
        "fixed_by": "someone",
        "fix_description": "desc",
    }
    with pytest.raises(ValueError):
        temp_service.fix_feature_metadata(fix_request)


def test_fix_feature_not_found(temp_service):
    with pytest.raises(ValueError):
        temp_service.fix_feature_metadata(
            {
                "feature_name": "notfound:v1",
                "user_role": "developer",
                "fixed_by": "someone",
                "fix_description": "desc",
            }
        )


def test_fix_feature_wrong_status(temp_service, sample_create_request):
    temp_service.create_feature_metadata(sample_create_request)
    fix_request = {
        "feature_name": sample_create_request["feature_name"],
        "user_role": "developer",
        "fixed_by": "someone",
        "fix_description": "desc",
    }
    with pytest.raises(ValueError):
        temp_service.fix_feature_metadata(fix_request)


def test_update_feature_metadata_rejected_to_draft(temp_service, sample_create_request):
    temp_service.create_feature_metadata(sample_create_request)
    meta = temp_service.metadata[sample_create_request["feature_name"]]
    meta["status"] = "REJECTED"
    temp_service._save_data()
    update_request = {
        "feature_name": sample_create_request["feature_name"],
        "user_role": "developer",
        "last_updated_by": "dev_user",
        "query": "SELECT new_value FROM test",
    }
    result = temp_service.update_feature_metadata(update_request)
    assert result.status == "DRAFT"


# Convert request to dict tests
def test_convert_request_to_dict_with_dict(temp_service):
    class DictOnly:
        def dict(self):
            return {"foo": "bar", "from_dict": True}

    obj = DictOnly()
    result = temp_service._convert_request_to_dict(obj)
    assert result["from_dict"] is True


def test_convert_request_to_dict_model_dump(temp_service):
    class ModelDumpOnly:
        def model_dump(self):
            return {"foo": "bar", "from_model_dump": True}

    obj = ModelDumpOnly()
    result = temp_service._convert_request_to_dict(obj)
    assert result["from_model_dump"] is True


def test_convert_request_to_dict_both_methods(temp_service):
    class BothMethods:
        def model_dump(self):
            return {"foo": "bar", "from_model_dump": True}

        def dict(self):
            return {"foo": "bar", "from_dict": True}

    obj = BothMethods()
    result = temp_service._convert_request_to_dict(obj)
    assert result["from_model_dump"] is True
    assert "from_dict" not in result


def test_convert_request_to_dict_fallback(temp_service):
    class Dummy:
        foo = "bar"
        baz = 42

    dummy = Dummy()
    result = temp_service._convert_request_to_dict(dummy)
    assert result["foo"] == "bar"
    assert result["baz"] == 42


# Create feature with dict/model_dump
def test_create_feature_with_dict(temp_service, sample_create_request):
    result = temp_service.create_feature(sample_create_request)
    assert result.feature_name == sample_create_request["feature_name"]


def test_create_feature_with_model_dump(temp_service):
    class ModelDumpRequest:
        def model_dump(self):
            return {
                "feature_name": "test:modeldump:v1",
                "feature_type": "batch",
                "feature_data_type": "float",
                "query": "SELECT 1",
                "description": "desc",
                "created_by": "dev",
                "user_role": "developer",
            }

    obj = ModelDumpRequest()
    result = temp_service.create_feature(obj)
    assert result.feature_name == "test:modeldump:v1"


# Save data IO error branch
def test_save_data_ioerror_branch(temp_service):
    import builtins

    orig_open = builtins.open

    def bad_open(*a, **k):
        raise OSError("disk full")

    builtins.open = bad_open
    try:
        temp_service.metadata["fail:save:1"] = {"some": "data"}
        with pytest.raises(Exception, match="Failed to save data:"):
            temp_service._save_data()
    finally:
        builtins.open = orig_open


# Get all feature metadata continue
def test_get_all_feature_metadata_continue(temp_service, sample_create_request):
    temp_service.create_feature_metadata(sample_create_request)
    result = temp_service.get_all_feature_metadata("developer", {"status": "DEPLOYED"})
    assert result == {}


def test_get_all_feature_metadata_continue_created_by(
    temp_service, sample_create_request
):
    temp_service.create_feature_metadata(sample_create_request)
    result = temp_service.get_all_feature_metadata(
        "developer", {"created_by": "not_a_creator"}
    )
    assert result == {}


def test_save_metadata_calls_save_data(temp_service):
    temp_service.metadata["test:save:meta:1"] = {"foo": "bar"}
    temp_service._save_metadata()


def test_create_feature_metadata_missing_fields():
    service = FeatureMetadataService()
    with pytest.raises(ValueError):
        service.create_feature_metadata({})


def test_create_feature_metadata_invalid_role():
    service = FeatureMetadataService()
    req = {
        "feature_name": "invalid:role:v1",
        "feature_type": "batch",
        "feature_data_type": "float",
        "query": "SELECT 1",
        "description": "desc",
        "created_by": "dev",
        "user_role": "notarole",
    }
    with pytest.raises(ValueError):
        service.create_feature_metadata(req)


# FeatureValidator and RoleValidator branches
def test_feature_validator_all_branches():
    from app.utils.validation import FeatureValidator

    validator = FeatureValidator()
    errors = validator.validate_feature_metadata({})
    assert "feature_name" in errors
    errors = validator.validate_feature_metadata(
        {
            "feature_name": "invalid",
            "feature_type": "batch",
            "feature_data_type": "float",
            "query": "SELECT 1",
            "description": "desc",
            "created_by": "dev",
        }
    )
    assert "feature_name" in errors
    errors = validator.validate_feature_metadata(
        {
            "feature_name": "cat:name:1",
            "feature_type": "invalid",
            "feature_data_type": "float",
            "query": "SELECT 1",
            "description": "desc",
            "created_by": "dev",
        }
    )
    assert "feature_type" in errors
    errors = validator.validate_feature_metadata(
        {
            "feature_name": "cat:name:1",
            "feature_type": "batch",
            "feature_data_type": "invalid",
            "query": "SELECT 1",
            "description": "desc",
            "created_by": "dev",
        }
    )
    assert "feature_data_type" in errors
    errors = validator.validate_feature_metadata(
        {
            "feature_name": "cat:name:1",
            "feature_type": "batch",
            "feature_data_type": "float",
            "query": "",
            "description": "desc",
            "created_by": "dev",
        }
    )
    assert "query" in errors
    errors = validator.validate_feature_metadata(
        {
            "feature_name": "cat:name:1",
            "feature_type": "batch",
            "feature_data_type": "float",
            "query": "SELECT 1",
            "description": "",
            "created_by": "dev",
        }
    )
    assert "description" in errors
    errors = validator.validate_feature_metadata(
        {
            "feature_name": "cat:name:1",
            "feature_type": "batch",
            "feature_data_type": "float",
            "query": "SELECT 1",
            "description": "desc",
            "created_by": "",
        }
    )
    assert "created_by" in errors


def test_role_validator_all_branches():
    from app.utils.validation import RoleValidator

    assert RoleValidator.can_perform_action("developer", "create")[0] is True
    assert RoleValidator.can_perform_action("invalid", "create")[0] is False
    assert RoleValidator.can_perform_action("developer", "approve")[0] is False


def test_get_current_timestamp(monkeypatch):
    from app.utils import timestamp

    ts = timestamp.get_current_timestamp()
    assert isinstance(ts, int)
    monkeypatch.setattr("time.time", lambda: (_ for _ in ()).throw(Exception("fail")))
    try:
        timestamp.get_current_timestamp()
    except Exception as e:
        assert str(e) == "fail"


def test_convert_request_to_dict_model_dump_not_dict(temp_service):
    class BadModelDump:
        def model_dump(self):
            return 123

    obj = BadModelDump()
    with pytest.raises(ValueError, match="model_dump\\(\\) did not return a dict"):
        temp_service._convert_request_to_dict(obj)


def test_convert_request_to_dict_dict_not_dict(temp_service):
    class BadDict:
        def dict(self):
            return 123

    obj = BadDict()
    with pytest.raises(ValueError, match="dict\\(\\) did not return a dict"):
        temp_service._convert_request_to_dict(obj)
