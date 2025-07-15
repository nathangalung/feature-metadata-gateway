import json
import threading
from pathlib import Path
from typing import Any

from app.models.request import FeatureMetadata
from app.utils.timestamp import get_current_timestamp
from app.utils.validation import FeatureValidator, RoleValidator


# Base service class
class FeatureService:
    """Base feature service."""

    pass


# Feature metadata management
class FeatureMetadataService(FeatureService):
    """Manage feature metadata."""

    def __init__(self, data_file: str = "data/feature_metadata.json"):
        self.data_file = Path(data_file)
        self.data_file.parent.mkdir(exist_ok=True)
        self._lock = threading.RLock()
        self.metadata: dict[str, dict[str, Any]] = {}
        self.validator = FeatureValidator()
        self._load_data()

    def _load_data(self) -> None:
        # Load metadata from file
        try:
            if self.data_file.exists():
                with open(self.data_file) as f:
                    data = json.load(f)
                    self.metadata = data if isinstance(data, dict) else {}
            else:
                self.metadata = {}
        except (OSError, json.JSONDecodeError) as e:
            print(f"Error loading data: {e}")
            self.metadata = {}

    def _save_data(self) -> None:
        # Save metadata to file
        try:
            with open(self.data_file, "w") as f:
                json.dump(self.metadata, f, indent=2)
        except OSError as e:
            raise Exception(f"Failed to save data: {e}") from e

    def _convert_request_to_dict(
        self, request: dict[str, Any] | object
    ) -> dict[str, Any]:
        # Convert request to dict
        if isinstance(request, dict):
            return request
        elif hasattr(request, "model_dump"):
            result = request.model_dump()
            if isinstance(result, dict):
                return result
            raise ValueError("model_dump() did not return a dict")
        elif hasattr(request, "dict"):
            result = request.dict()
            if isinstance(result, dict):
                return result
            raise ValueError("dict() did not return a dict")
        else:
            out: dict[str, Any] = {}
            for key in dir(request):
                if (
                    isinstance(key, str)
                    and not key.startswith("_")
                    and not callable(getattr(request, key))
                ):
                    out[str(key)] = getattr(request, key)
            return out

    def create_feature_metadata(self, request_data: dict[str, Any]) -> FeatureMetadata:
        # Create feature metadata
        with self._lock:
            feature_name = str(request_data.get("feature_name", ""))
            user_role = str(request_data.get("user_role", ""))
            can_create, error_msg = RoleValidator.can_perform_action(
                user_role, "create"
            )
            if not can_create:
                raise ValueError(error_msg)
            if feature_name in self.metadata:
                raise ValueError(f"Feature {feature_name} already exists")
            validation_errors = FeatureValidator.validate_feature_metadata(request_data)
            if validation_errors:
                error_details = "; ".join(
                    [f"{k}: {v}" for k, v in validation_errors.items()]
                )
                raise ValueError(f"Validation errors: {error_details}")
            current_time = int(get_current_timestamp())
            metadata_dict = {
                "feature_name": feature_name,
                "feature_type": request_data["feature_type"],
                "feature_data_type": request_data["feature_data_type"],
                "query": request_data["query"],
                "description": request_data["description"],
                "status": "DRAFT",
                "created_time": current_time,
                "updated_time": current_time,
                "created_by": request_data["created_by"],
                "last_updated_by": None,
            }
            self.metadata[feature_name] = metadata_dict
            self._save_data()
            return FeatureMetadata(**metadata_dict)

    def get_all_feature_metadata(
        self, user_role: str, filters: dict[str, Any] | None = None
    ) -> dict[str, FeatureMetadata]:
        # Get metadata with fuzzy filter
        import difflib

        def is_exact_match(meta: dict[str, Any], filters: dict[str, Any]) -> bool:
            for key, value in filters.items():
                if key == "query":
                    continue
                if key in meta and str(meta[key]) != str(value):
                    return False
            return True

        def similarity(a: str, b: str) -> float:
            return difflib.SequenceMatcher(None, a, b).ratio()

        with self._lock:
            result: dict[str, FeatureMetadata] = {}
            if not filters:
                for feature_name, metadata_dict in self.metadata.items():
                    result[feature_name] = FeatureMetadata(**metadata_dict)
                return result

            # Try exact match first
            for feature_name, metadata_dict in self.metadata.items():
                if is_exact_match(metadata_dict, filters):
                    result[feature_name] = FeatureMetadata(**metadata_dict)

            if result:
                return result

            # Fuzzy match if no exact
            threshold = 0.7
            for feature_name, metadata_dict in self.metadata.items():
                match_score = 0.0
                match_fields = 0
                for key, value in filters.items():
                    if key == "query":
                        continue
                    if key in metadata_dict and metadata_dict[key] is not None:
                        match_fields += 1
                        score = similarity(str(metadata_dict[key]), str(value))
                        match_score += score
                if match_fields > 0 and (match_score / match_fields) >= threshold:
                    result[feature_name] = FeatureMetadata(**metadata_dict)
            return result

    def get_feature_metadata(
        self, feature_name: str, user_role: str = "developer"
    ) -> FeatureMetadata:
        # Get single metadata
        with self._lock:
            if not isinstance(feature_name, str) or feature_name not in self.metadata:
                raise ValueError(f"Feature {feature_name} not found")
            metadata_dict = self.metadata[feature_name].copy()
            return FeatureMetadata(**metadata_dict)

    def update_feature_metadata(self, request_data: dict[str, Any]) -> FeatureMetadata:
        # Update metadata, reset status
        with self._lock:
            feature_name = request_data.get("feature_name")
            user_role = str(request_data.get("user_role", ""))
            if feature_name not in self.metadata:
                raise ValueError(f"Feature {feature_name} not found")
            can_update, error_msg = RoleValidator.can_perform_action(
                user_role, "update"
            )
            if not can_update:
                raise ValueError(error_msg)
            metadata = self.metadata[feature_name]
            if metadata.get("status") == "DEPLOYED":
                raise ValueError("Cannot update DEPLOYED feature")
            for field in request_data:
                if field in metadata and request_data[field] is not None:
                    metadata[field] = request_data[field]
            metadata["status"] = "DRAFT"
            metadata["updated_time"] = int(get_current_timestamp())
            self.metadata[feature_name] = metadata
            self._save_data()
            return FeatureMetadata(**metadata)

    def delete_feature_metadata(self, request_data: dict[str, Any]) -> FeatureMetadata:
        # Delete feature metadata
        with self._lock:
            feature_name = request_data.get("feature_name")
            user_role = str(request_data.get("user_role", ""))
            can_delete, error_msg = RoleValidator.can_perform_action(
                user_role, "delete"
            )
            if not can_delete:
                raise ValueError(error_msg)
            if feature_name not in self.metadata:
                raise ValueError(f"Feature {feature_name} not found")
            metadata = self.metadata[feature_name]
            if metadata.get("status") == "DEPLOYED":
                raise ValueError("Cannot delete DEPLOYED feature")
            metadata["status"] = "DELETED"
            metadata["deleted_time"] = int(get_current_timestamp())
            metadata["deleted_by"] = request_data.get("deleted_by")
            self.metadata[feature_name] = metadata
            self._save_data()
            return FeatureMetadata(**metadata)

    def submit_test_feature_metadata(
        self, request_data: dict[str, Any]
    ) -> FeatureMetadata:
        # Mark ready for testing
        with self._lock:
            feature_name = request_data.get("feature_name")
            user_role = str(request_data.get("user_role", ""))
            can_submit, error_msg = RoleValidator.can_perform_action(
                user_role, "submit_test"
            )
            if not can_submit:
                raise ValueError(error_msg)
            if feature_name not in self.metadata:
                raise ValueError(f"Feature {feature_name} not found")
            metadata = self.metadata[feature_name]
            if metadata.get("status") != "DRAFT":
                raise ValueError("Feature must be in DRAFT status")
            metadata["status"] = "READY_FOR_TESTING"
            metadata["updated_time"] = int(get_current_timestamp())
            metadata["submitted_by"] = request_data.get("submitted_by")
            self.metadata[feature_name] = metadata
            self._save_data()
            return FeatureMetadata(**metadata)

    def test_feature_metadata(self, request_data: dict[str, Any]) -> FeatureMetadata:
        # Test feature metadata
        with self._lock:
            feature_name = request_data.get("feature_name")
            user_role = str(request_data.get("user_role", ""))
            can_test, error_msg = RoleValidator.can_perform_action(user_role, "test")
            if not can_test:
                raise ValueError(error_msg)
            if feature_name not in self.metadata:
                raise ValueError(f"Feature {feature_name} not found")
            metadata = self.metadata[feature_name]
            if metadata.get("status") != "READY_FOR_TESTING":
                raise ValueError("Feature must be in READY_FOR_TESTING status")
            test_result = request_data.get("test_result")
            if test_result not in ["TEST_SUCCEEDED", "TEST_FAILED"]:
                raise ValueError("Invalid test result")
            metadata["status"] = test_result
            metadata["tested_by"] = request_data.get("tested_by")
            metadata["tested_time"] = int(get_current_timestamp())
            metadata["test_result"] = test_result
            metadata["test_notes"] = request_data.get("test_notes")
            self.metadata[feature_name] = metadata
            self._save_data()
            return FeatureMetadata(**metadata)

    def approve_feature_metadata(self, request_data: dict[str, Any]) -> FeatureMetadata:
        # Approve feature metadata
        with self._lock:
            feature_name = request_data.get("feature_name")
            user_role = str(request_data.get("user_role", ""))
            can_approve, error_msg = RoleValidator.can_perform_action(
                user_role, "approve"
            )
            if not can_approve:
                raise ValueError(error_msg)
            if feature_name not in self.metadata:
                raise ValueError(f"Feature {feature_name} not found")
            metadata = self.metadata[feature_name]
            if metadata.get("status") != "TEST_SUCCEEDED":
                raise ValueError("Feature must be in TEST_SUCCEEDED status")
            metadata["status"] = "DEPLOYED"
            metadata["approved_by"] = request_data.get("approved_by")
            metadata["approved_time"] = int(get_current_timestamp())
            metadata["deployed_by"] = request_data.get("approved_by")
            metadata["deployed_time"] = int(get_current_timestamp())
            self.metadata[feature_name] = metadata
            self._save_data()
            return FeatureMetadata(**metadata)

    def reject_feature_metadata(self, request_data: dict[str, Any]) -> FeatureMetadata:
        # Reject feature metadata
        with self._lock:
            feature_name = request_data.get("feature_name")
            user_role = str(request_data.get("user_role", ""))
            can_reject, error_msg = RoleValidator.can_perform_action(
                user_role, "reject"
            )
            if not can_reject:
                raise ValueError(error_msg)
            if feature_name not in self.metadata:
                raise ValueError(f"Feature {feature_name} not found")
            metadata = self.metadata[feature_name]
            if metadata.get("status") != "TEST_SUCCEEDED":
                raise ValueError("Feature must be in TEST_SUCCEEDED status")
            metadata["status"] = "REJECTED"
            metadata["rejected_by"] = request_data.get("rejected_by")
            metadata["rejection_reason"] = request_data.get("rejection_reason")
            metadata["updated_time"] = int(get_current_timestamp())
            self.metadata[feature_name] = metadata
            self._save_data()
            return FeatureMetadata(**metadata)
