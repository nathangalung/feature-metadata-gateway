"""Feature metadata service."""

import json
import threading
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from app.models.request import (
    FeatureMetadata, CreateFeatureRequest, UpdateFeatureRequest,
    DeleteFeatureRequest, ReadyTestRequest, TestFeatureRequest,
    ApproveFeatureRequest, RejectFeatureRequest, FixFeatureRequest
)
from app.utils.timestamp import get_current_timestamp
from app.utils.validation import FeatureValidator, RoleValidator
from app.utils.constants import CRITICAL_FIELDS

class FeatureService:
    """Base feature service class."""
    pass

class FeatureMetadataService(FeatureService):
    """Service for managing feature metadata."""

    def __init__(self, data_file: str = "data/feature_metadata.json"):
        self.data_file = Path(data_file)
        self.metadata_file = self.data_file
        self.data_file.parent.mkdir(exist_ok=True)
        self._lock = threading.RLock()
        self.metadata: Dict[str, Dict[str, Any]] = {}
        self.validator = FeatureValidator()
        self._load_data()

    def _load_data(self) -> None:
        try:
            if self.data_file.exists():
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.metadata = data if isinstance(data, dict) else {}
            else:
                self.metadata = {}
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading data: {e}")
            self.metadata = {}

    def _save_data(self) -> None:
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.metadata, f, indent=2)
        except IOError as e:
            raise Exception(f"Failed to save data: {e}")

    def _save_metadata(self) -> None:
        return self._save_data()

    def _convert_request_to_dict(self, request: Union[Dict[str, Any], object]) -> Dict[str, Any]:
        if isinstance(request, dict):
            return request
        elif hasattr(request, 'model_dump'):
            return request.model_dump()
        elif hasattr(request, 'dict'):
            return request.dict()
        else:
            return {key: getattr(request, key) for key in dir(request)
                    if not key.startswith('_') and not callable(getattr(request, key))}

    def create_feature(self, request: Union[CreateFeatureRequest, Dict[str, Any]]) -> FeatureMetadata:
        request_data = self._convert_request_to_dict(request)
        return self.create_feature_metadata(request_data)

    def create_feature_metadata(self, request_data: Dict[str, Any]) -> FeatureMetadata:
        with self._lock:
            feature_name = request_data.get('feature_name')
            user_role = request_data.get('user_role')
            can_create, error_msg = RoleValidator.can_perform_action(user_role, 'create')
            if not can_create:
                raise ValueError(error_msg)
            if feature_name in self.metadata:
                raise ValueError(f"Feature {feature_name} already exists")
            validation_errors = FeatureValidator.validate_feature_metadata(request_data)
            if validation_errors:
                error_details = "; ".join([f"{k}: {v}" for k, v in validation_errors.items()])
                raise ValueError(f"Validation errors: {error_details}")
            current_time = get_current_timestamp()
            metadata_dict = {
                'feature_name': feature_name,
                'feature_type': request_data['feature_type'],
                'feature_data_type': request_data['feature_data_type'],
                'query': request_data['query'],
                'description': request_data['description'],
                'status': 'DRAFT',
                'created_time': current_time,
                'updated_time': current_time,
                'created_by': request_data['created_by'],
                'last_updated_by': None
            }
            self.metadata[feature_name] = metadata_dict
            self._save_data()
            return FeatureMetadata(**metadata_dict)

    def get_feature_metadata(self, feature_name: str, user_role: str = "developer") -> FeatureMetadata:
        with self._lock:
            if feature_name not in self.metadata:
                raise ValueError(f"Feature {feature_name} not found")
            metadata_dict = self.metadata[feature_name].copy()
            return FeatureMetadata(**metadata_dict)

    def get_all_feature_metadata(self, user_role: str, filters: Optional[Dict[str, Any]] = None) -> Dict[str, FeatureMetadata]:
        with self._lock:
            result = {}
            for feature_name, metadata_dict in self.metadata.items():
                if filters:
                    if 'status' in filters and metadata_dict.get('status') != filters['status']:
                        continue
                    if 'feature_type' in filters and metadata_dict.get('feature_type') != filters['feature_type']:
                        continue
                    if 'created_by' in filters and metadata_dict.get('created_by') != filters['created_by']:
                        continue
                result[feature_name] = FeatureMetadata(**metadata_dict)
            return result

    def get_all_features(self, user_role: str) -> list:
        return list(self.metadata.keys())

    def get_not_deployed_features(self, user_role: str) -> list:
        return [name for name, meta in self.metadata.items() if meta.get('status') != "DEPLOYED"]

    def update_feature_metadata(self, request_data: Dict[str, Any]) -> FeatureMetadata:
        with self._lock:
            feature_name = request_data.get('feature_name')
            user_role = request_data.get('user_role')
            if feature_name not in self.metadata:
                raise ValueError(f"Feature {feature_name} not found")
            can_update, error_msg = RoleValidator.can_perform_action(user_role, 'update')
            if not can_update:
                raise ValueError(error_msg)
            metadata = self.metadata[feature_name]
            if metadata.get('status') == "DEPLOYED":
                raise ValueError("Cannot update DEPLOYED feature")
            critical_changed = False
            for field in CRITICAL_FIELDS:
                if field in request_data and request_data[field] is not None and request_data[field] != metadata.get(field):
                    critical_changed = True
                    metadata[field] = request_data[field]
            for field in ['description', 'status', 'last_updated_by']:
                if field in request_data and request_data[field] is not None:
                    metadata[field] = request_data[field]
            if critical_changed:
                # If status is REJECTED, reset to DRAFT; else, keep READY_FOR_TESTING if already tested
                if metadata.get('status') == "REJECTED":
                    metadata['status'] = "DRAFT"
                elif metadata.get('status') in ("TEST_SUCCEEDED", "READY_FOR_TESTING"):
                    metadata['status'] = "READY_FOR_TESTING"
                else:
                    metadata['status'] = "DRAFT"
            metadata['updated_time'] = get_current_timestamp()
            self.metadata[feature_name] = metadata
            self._save_data()
            return FeatureMetadata(**metadata)

    def delete_feature_metadata(self, request_data: Dict[str, Any]) -> FeatureMetadata:
        with self._lock:
            feature_name = request_data.get('feature_name')
            user_role = request_data.get('user_role')
            can_delete, error_msg = RoleValidator.can_perform_action(user_role, 'delete')
            if not can_delete:
                raise ValueError(error_msg)
            if feature_name not in self.metadata:
                raise ValueError(f"Feature {feature_name} not found")
            metadata = self.metadata[feature_name]
            if metadata.get('status') == "DEPLOYED":
                raise ValueError("Cannot delete DEPLOYED feature")
            metadata['status'] = "DELETED"
            metadata['deleted_time'] = get_current_timestamp()
            metadata['deleted_by'] = request_data.get('deleted_by')
            self.metadata[feature_name] = metadata
            self._save_data()
            return FeatureMetadata(**metadata)

    def ready_test_feature_metadata(self, request_data: Dict[str, Any]) -> FeatureMetadata:
        with self._lock:
            feature_name = request_data.get('feature_name')
            user_role = request_data.get('user_role')
            can_ready, error_msg = RoleValidator.can_perform_action(user_role, 'ready_for_testing')
            if not can_ready:
                raise ValueError(error_msg)
            if feature_name not in self.metadata:
                raise ValueError(f"Feature {feature_name} not found")
            metadata = self.metadata[feature_name]
            if metadata.get('status') != "DRAFT":
                raise ValueError("Feature must be in DRAFT status")
            metadata['status'] = "READY_FOR_TESTING"
            metadata['updated_time'] = get_current_timestamp()
            metadata['submitted_by'] = request_data.get('submitted_by')
            self.metadata[feature_name] = metadata
            self._save_data()
            return FeatureMetadata(**metadata)

    def test_feature_metadata(self, request_data: Dict[str, Any]) -> FeatureMetadata:
        with self._lock:
            feature_name = request_data.get('feature_name')
            user_role = request_data.get('user_role')
            can_test, error_msg = RoleValidator.can_perform_action(user_role, 'test')
            if not can_test:
                raise ValueError(error_msg)
            if feature_name not in self.metadata:
                raise ValueError(f"Feature {feature_name} not found")
            metadata = self.metadata[feature_name]
            if metadata.get('status') != "READY_FOR_TESTING":
                raise ValueError("Feature must be in READY_FOR_TESTING status")
            test_result = request_data.get('test_result')
            if test_result not in ["TEST_SUCCEEDED", "TEST_FAILED"]:
                raise ValueError("Invalid test result")
            metadata['status'] = test_result
            metadata['tested_by'] = request_data.get('tested_by')
            metadata['tested_time'] = get_current_timestamp()
            metadata['test_result'] = test_result
            metadata['test_notes'] = request_data.get('test_notes')
            self.metadata[feature_name] = metadata
            self._save_data()
            return FeatureMetadata(**metadata)

    def approve_feature_metadata(self, request_data: dict[str, Any]) -> FeatureMetadata:
        with self._lock:
            feature_name = request_data.get('feature_name')
            user_role = request_data.get('user_role')
            can_approve, error_msg = RoleValidator.can_perform_action(user_role, 'approve')
            if not can_approve:
                raise ValueError(error_msg)
            if feature_name not in self.metadata:
                raise ValueError(f"Feature {feature_name} not found")
            metadata = self.metadata[feature_name]
            if metadata.get('status') != "TEST_SUCCEEDED":
                raise ValueError("Feature must be in TEST_SUCCEEDED status")
            metadata['status'] = "DEPLOYED"
            metadata['approved_by'] = request_data.get('approved_by')
            metadata['approved_time'] = get_current_timestamp()
            metadata['deployed_by'] = request_data.get('approved_by')
            metadata['deployed_time'] = get_current_timestamp()
            self.metadata[feature_name] = metadata
            self._save_data()
            return FeatureMetadata(**metadata)

    def reject_feature_metadata(self, request_data: dict[str, Any]) -> FeatureMetadata:
        with self._lock:
            feature_name = request_data.get('feature_name')
            user_role = request_data.get('user_role')
            can_reject, error_msg = RoleValidator.can_perform_action(user_role, 'reject')
            if not can_reject:
                raise ValueError(error_msg)
            if feature_name not in self.metadata:
                raise ValueError(f"Feature {feature_name} not found")
            metadata = self.metadata[feature_name]
            if metadata.get('status') != "TEST_SUCCEEDED":
                raise ValueError("Feature must be in TEST_SUCCEEDED status")
            metadata['status'] = "REJECTED"
            metadata['rejected_by'] = request_data.get('rejected_by')
            metadata['rejection_reason'] = request_data.get('rejection_reason')
            metadata['updated_time'] = get_current_timestamp()
            self.metadata[feature_name] = metadata
            self._save_data()
            return FeatureMetadata(**metadata)

    def fix_feature_metadata(self, request_data: Dict[str, Any]) -> FeatureMetadata:
        with self._lock:
            feature_name = request_data.get('feature_name')
            user_role = request_data.get('user_role')
            can_fix, error_msg = RoleValidator.can_perform_action(user_role, 'fix')
            if not can_fix:
                raise ValueError(error_msg)
            if feature_name not in self.metadata:
                raise ValueError(f"Feature {feature_name} not found")
            metadata = self.metadata[feature_name]
            if metadata.get('status') not in ("TEST_FAILED", "REJECTED"):
                raise ValueError("Feature must be in TEST_FAILED or REJECTED status")
            metadata['status'] = "DRAFT"
            metadata['fixed_by'] = request_data.get('fixed_by')
            metadata['fix_description'] = request_data.get('fix_description')
            metadata['updated_time'] = get_current_timestamp()
            # Remove test/failure/rejection fields
            for field in ["tested_by", "tested_time", "test_result", "test_notes", "rejected_by", "rejection_reason"]:
                if field in metadata:
                    metadata.pop(field, None)
            self.metadata[feature_name] = metadata
            self._save_data()
            return FeatureMetadata(**metadata)

    def get_deployed_features(self, user_role: str) -> List[str]:
        with self._lock:
            return [name for name, meta in self.metadata.items() if meta.get('status') == "DEPLOYED"]

    def get_features_by_status(self, status: str, user_role: str) -> List[str]:
        with self._lock:
            return [name for name, meta in self.metadata.items() if meta.get('status') == status]