import tempfile
import threading
from pathlib import Path
from unittest.mock import patch

import pytest

from app.services.feature_service import FeatureMetadataService


@pytest.fixture
def temp_service():
    temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
    temp_path = Path(temp_file.name)
    temp_file.close()
    service = FeatureMetadataService(str(temp_path))
    yield service
    if temp_path.exists():
        temp_path.unlink()


class TestFeatureMetadataService:
    def test_init_default_path(self):
        with (
            patch("pathlib.Path.mkdir"),
            patch("pathlib.Path.exists", return_value=False),
        ):
            service = FeatureMetadataService()
            assert service.data_file.name == "feature_metadata.json"

    def test_init_custom_path(self, clean_data_file):
        service = FeatureMetadataService(clean_data_file)
        assert str(service.data_file) == clean_data_file

    def test_load_data_not_exists(self, temp_service):
        assert temp_service.metadata == {}

    def test_load_data_invalid_json(self):
        temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
        temp_path = Path(temp_file.name)
        with open(temp_path, "w") as f:
            f.write("invalid json")
        service = FeatureMetadataService(str(temp_path))
        assert service.metadata == {}
        temp_path.unlink()

    def test_save_data_io_error(self, temp_service):
        with patch("builtins.open", side_effect=OSError("Mock IO error")):
            with pytest.raises(Exception, match="Failed to save data"):
                temp_service._save_data()

    def test_convert_request_to_dict_with_dict(self, temp_service):
        class DictOnly:
            def dict(self):
                return {"foo": "bar", "from_dict": True}

        obj = DictOnly()
        result = temp_service._convert_request_to_dict(obj)
        assert result["from_dict"] is True

    def test_convert_request_to_dict_model_dump(self, temp_service):
        class ModelDumpOnly:
            def model_dump(self):
                return {"foo": "bar", "from_model_dump": True}

        obj = ModelDumpOnly()
        result = temp_service._convert_request_to_dict(obj)
        assert result["from_model_dump"] is True

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

    def test_convert_request_to_dict_fallback(self, temp_service):
        class Dummy:
            foo = "bar"
            baz = 42

        dummy = Dummy()
        result = temp_service._convert_request_to_dict(dummy)
        assert result["foo"] == "bar"
        assert result["baz"] == 42

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
        with pytest.raises(ValueError):
            temp_service.create_feature_metadata(request_data)

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

    def test_get_feature_not_found(self, temp_service):
        with pytest.raises(ValueError, match="not found"):
            temp_service.get_feature_metadata("nonexistent:feature:v1")

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

    def test_get_all_features_fuzzy(
        self, service_with_multiple_features, multiple_feature_data
    ):
        # Fuzzy match: misspelled filter
        result = service_with_multiple_features.get_all_feature_metadata(
            "developer", {"feature_type": "batc"}
        )
        assert isinstance(result, dict)

    def test_update_feature_not_found(self, temp_service):
        request_data = {
            "feature_name": "nonexistent:feature:v1",
            "user_role": "developer",
            "last_updated_by": "test_user",
        }
        with pytest.raises(ValueError, match="not found"):
            temp_service.update_feature_metadata(request_data)

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
        assert result.status == "DRAFT"

    def test_update_metadata_fields(self, temp_service, sample_feature_metadata):
        temp_service.metadata[sample_feature_metadata["feature_name"]] = (
            sample_feature_metadata.copy()
        )
        temp_service._save_data()
        request_data = {
            "feature_name": sample_feature_metadata["feature_name"],
            "user_role": "developer",
            "last_updated_by": "test_user",
            "description": "Updated description",
            "feature_type": "batch",
            "feature_data_type": "float",
            "query": "SELECT updated FROM test",
        }
        result = temp_service.update_feature_metadata(request_data)
        assert result.description == "Updated description"
        assert result.status == "DRAFT"

    def test_update_critical_field(self, temp_service, sample_feature_metadata):
        temp_service.metadata[sample_feature_metadata["feature_name"]] = (
            sample_feature_metadata.copy()
        )
        temp_service._save_data()
        request_data = {
            "feature_name": sample_feature_metadata["feature_name"],
            "user_role": "developer",
            "last_updated_by": "test_user",
            "query": "SELECT updated FROM test",
        }
        result = temp_service.update_feature_metadata(request_data)
        assert result.query == "SELECT updated FROM test"
        assert result.status == "DRAFT"

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

    def test_delete_feature_not_found(self, temp_service):
        request_data = {
            "feature_name": "notfound:v1",
            "user_role": "developer",
            "deleted_by": "test_user",
            "deletion_reason": "test",
        }
        with pytest.raises(ValueError, match="not found"):
            temp_service.delete_feature_metadata(request_data)

    def test_submit_test_invalid_transition(
        self, temp_service, sample_feature_metadata
    ):
        deployed_metadata = sample_feature_metadata.copy()
        deployed_metadata["status"] = "DEPLOYED"
        temp_service.metadata[deployed_metadata["feature_name"]] = deployed_metadata
        temp_service._save_data()
        request_data = {
            "feature_name": deployed_metadata["feature_name"],
            "user_role": "developer",
            "submitted_by": "test_user",
        }
        with pytest.raises(ValueError):
            temp_service.submit_test_feature_metadata(request_data)

    def test_submit_test_permission_denied(self, temp_service, sample_create_request):
        temp_service.create_feature_metadata(sample_create_request)
        submit_request = {
            "feature_name": sample_create_request["feature_name"],
            "user_role": "notarole",
            "submitted_by": "someone",
        }
        with pytest.raises(ValueError):
            temp_service.submit_test_feature_metadata(submit_request)

    def test_submit_test_feature_not_found(self, temp_service):
        with pytest.raises(ValueError):
            temp_service.submit_test_feature_metadata(
                {
                    "feature_name": "notfound:v1",
                    "user_role": "developer",
                    "submitted_by": "someone",
                }
            )

    def test_submit_test_feature_wrong_status(
        self, temp_service, sample_create_request
    ):
        temp_service.create_feature_metadata(sample_create_request)
        temp_service.metadata[sample_create_request["feature_name"]][
            "status"
        ] = "READY_FOR_TESTING"
        temp_service._save_data()
        submit_request = {
            "feature_name": sample_create_request["feature_name"],
            "user_role": "developer",
            "submitted_by": "someone",
        }
        with pytest.raises(ValueError):
            temp_service.submit_test_feature_metadata(submit_request)

    def test_test_feature_permission_denied(self, temp_service, sample_create_request):
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

    def test_test_feature_not_found(self, temp_service):
        test_request = {
            "feature_name": "notfound:v1",
            "user_role": "tester",
            "test_result": "TEST_SUCCEEDED",
            "tested_by": "someone",
        }
        with pytest.raises(ValueError):
            temp_service.test_feature_metadata(test_request)

    def test_test_feature_wrong_status(self, temp_service, sample_create_request):
        temp_service.create_feature_metadata(sample_create_request)
        test_request = {
            "feature_name": sample_create_request["feature_name"],
            "user_role": "tester",
            "test_result": "TEST_SUCCEEDED",
            "tested_by": "someone",
        }
        with pytest.raises(ValueError):
            temp_service.test_feature_metadata(test_request)

    def test_test_feature_invalid_result(self, temp_service, sample_create_request):
        temp_service.create_feature_metadata(sample_create_request)
        temp_service.metadata[sample_create_request["feature_name"]][
            "status"
        ] = "READY_FOR_TESTING"
        temp_service._save_data()
        test_request = {
            "feature_name": sample_create_request["feature_name"],
            "user_role": "tester",
            "test_result": "INVALID_RESULT",
            "tested_by": "someone",
        }
        with pytest.raises(ValueError):
            temp_service.test_feature_metadata(test_request)

    def test_approve_feature_permission_denied(
        self, temp_service, sample_create_request
    ):
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

    def test_approve_feature_not_found(self, temp_service):
        with pytest.raises(ValueError):
            temp_service.approve_feature_metadata(
                {
                    "feature_name": "notfound:v1",
                    "user_role": "approver",
                    "approved_by": "someone",
                }
            )

    def test_approve_feature_wrong_status(self, temp_service, sample_create_request):
        temp_service.create_feature_metadata(sample_create_request)
        approve_request = {
            "feature_name": sample_create_request["feature_name"],
            "user_role": "approver",
            "approved_by": "someone",
        }
        with pytest.raises(ValueError):
            temp_service.approve_feature_metadata(approve_request)

    def test_reject_feature_permission_denied(
        self, temp_service, sample_create_request
    ):
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

    def test_reject_feature_not_found(self, temp_service):
        request_data = {
            "feature_name": "notfound:v1",
            "user_role": "approver",
            "rejected_by": "someone",
            "rejection_reason": "reason",
        }
        with pytest.raises(ValueError):
            temp_service.reject_feature_metadata(request_data)

    def test_reject_feature_wrong_status(self, temp_service, sample_create_request):
        temp_service.create_feature_metadata(sample_create_request)
        reject_request = {
            "feature_name": sample_create_request["feature_name"],
            "user_role": "approver",
            "rejected_by": "someone",
            "rejection_reason": "reason",
        }
        with pytest.raises(ValueError):
            temp_service.reject_feature_metadata(reject_request)

    def test_threading_safety(self, sample_create_request):
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


def test_load_data_unexpected_error(monkeypatch):
    monkeypatch.setattr("pathlib.Path.exists", lambda self: True)
    monkeypatch.setattr(
        "builtins.open", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("fail"))
    )
    with pytest.raises(RuntimeError, match="fail"):
        FeatureMetadataService("not_a_real_file.json")


def test_convert_request_to_dict_model_dump_not_dict(temp_service):
    class BadModelDump:
        def model_dump(self):
            return "notadict"

    with pytest.raises(ValueError, match="model_dump"):
        temp_service._convert_request_to_dict(BadModelDump())


def test_convert_request_to_dict_dict_not_dict(temp_service):
    class BadDict:
        def dict(self):
            return "notadict"

    with pytest.raises(ValueError, match="dict"):
        temp_service._convert_request_to_dict(BadDict())


def test_save_data_unexpected_error(temp_service):
    with patch("builtins.open", side_effect=RuntimeError("fail")):
        with pytest.raises(RuntimeError, match="fail"):
            temp_service._save_data()


def test_fuzzy_match_logic(temp_service):
    temp_service.metadata = {
        "fuzzy:match:1": {
            "feature_name": "fuzzy:match:1",
            "feature_type": "batch",
            "feature_data_type": "float",
            "query": "SELECT 1",
            "description": "desc",
            "status": "DRAFT",
            "created_time": 1,
            "updated_time": 1,
            "created_by": "dev",
        },
        "other:feature:1": {
            "feature_name": "other:feature:1",
            "feature_type": "real-time",
            "feature_data_type": "string",
            "query": "SELECT 2",
            "description": "desc2",
            "status": "DRAFT",
            "created_time": 2,
            "updated_time": 2,
            "created_by": "dev2",
        },
    }
    result = temp_service.get_all_feature_metadata(
        "developer", {"feature_type": "batc"}
    )
    assert "fuzzy:match:1" in result
    assert isinstance(result, dict)
