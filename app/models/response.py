from typing import Any

from pydantic import BaseModel, Field, validator

from app.models.request import FeatureMetadata
from app.utils.timestamp import get_current_timestamp


# Base response model
class BaseResponse(BaseModel):
    timestamp: int = Field(default_factory=get_current_timestamp)
    request_id: str | None = Field(None)


# Generic success response
class SuccessResponse(BaseResponse):
    success: bool = Field(True)
    message: str = Field(...)
    data: Any | None = Field(None)


# Error response model
class ErrorResponse(BaseResponse):
    success: bool = Field(False)
    error: str = Field(...)
    message: str = Field(...)
    details: dict[str, Any] | None = Field(None)


# Single feature metadata response
class FeatureMetadataResponse(BaseResponse):
    success: bool = Field(True)
    metadata: FeatureMetadata = Field(...)


# All feature metadata response
class AllMetadataResponse(BaseResponse):
    success: bool = Field(True)
    metadata: dict[str, FeatureMetadata] | list[FeatureMetadata] = Field(...)
    total_count: int = Field(...)

    def __init__(self, **data: Any) -> None:
        if "metadata" in data:
            metadata = data["metadata"]
            if isinstance(metadata, dict):
                data["metadata"] = list(metadata.values())
                if "total_count" not in data:
                    data["total_count"] = len(metadata)
            elif isinstance(metadata, list):
                if "total_count" not in data:
                    data["total_count"] = len(metadata)
            else:
                data["metadata"] = []
                data["total_count"] = 0
        else:
            data["metadata"] = []
            data["total_count"] = 0
        super().__init__(**data)

    @validator("metadata")
    def validate_metadata(
        cls, v: dict[str, FeatureMetadata] | list[FeatureMetadata]
    ) -> list[FeatureMetadata]:
        if isinstance(v, dict):
            return list(v.values())
        return v if v is not None else []


# Filtered feature metadata response
class FilteredMetadataResponse(BaseResponse):
    success: bool = Field(True)
    metadata: list[FeatureMetadata] = Field(...)
    total_count: int = Field(...)
    filters_applied: dict[str, Any] = Field(...)


# Create feature response
class CreateFeatureResponse(BaseResponse):
    success: bool = Field(True)
    message: str = Field("Feature created successfully")
    metadata: FeatureMetadata = Field(...)


# Update feature response
class UpdateFeatureResponse(BaseResponse):
    success: bool = Field(True)
    message: str = Field("Feature updated successfully")
    metadata: FeatureMetadata = Field(...)


# Delete feature response
class DeleteFeatureResponse(BaseResponse):
    success: bool = Field(True)
    message: str = Field("Feature deleted successfully")
    metadata: FeatureMetadata = Field(...)


# Workflow operation response
class WorkflowResponse(BaseResponse):
    success: bool = Field(True)
    message: str = Field(...)
    metadata: FeatureMetadata = Field(...)
    previous_status: str = Field(...)
    new_status: str = Field(...)


# Ready test response
class ReadyTestResponse(WorkflowResponse):
    message: str = Field("Feature submitted for testing")


# Test feature response
class TestFeatureResponse(WorkflowResponse):
    test_result: str = Field(...)
    test_notes: str | None = Field(None)


# Approve feature response
class ApproveFeatureResponse(WorkflowResponse):
    message: str = Field("Feature approved and deployed")
    approved_by: str = Field(...)


# Reject feature response
class RejectFeatureResponse(WorkflowResponse):
    message: str = Field("Feature rejected")
    rejection_reason: str = Field(...)


# Fix feature response
class FixFeatureResponse(WorkflowResponse):
    message: str = Field("Feature fixed and reset to DRAFT")
    fix_description: str = Field(...)


# Health check response
class HealthResponse(BaseResponse):
    status: str = Field("healthy")
    version: str = Field("1.0.0")
    uptime_seconds: int = Field(0)
    dependencies: dict[str, str] = Field(default_factory=dict)


# Validation response
class ValidationResponse(BaseResponse):
    is_valid: bool = Field(...)
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


# Status-based feature list response
class StatusListResponse(BaseResponse):
    success: bool = Field(True)
    status: str = Field(...)
    features: list[str] = Field(...)
    count: int = Field(...)

    def __init__(self, **data: Any) -> None:
        if "count" not in data and "features" in data:
            data["count"] = len(data["features"])
        super().__init__(**data)


# Deployed features list response
class DeployedFeaturesResponse(StatusListResponse):
    status: str = Field("DEPLOYED")


# Feature statistics response
class FeatureStatsResponse(BaseResponse):
    success: bool = Field(True)
    total_features: int = Field(...)
    features_by_status: dict[str, int] = Field(...)
    features_by_type: dict[str, int] = Field(...)
    features_by_data_type: dict[str, int] = Field(...)
    recent_activity: list[dict[str, Any]] = Field(default_factory=list)


# Bulk operation response
class BulkOperationResponse(BaseResponse):
    success: bool = Field(True)
    total_requested: int = Field(...)
    successful: int = Field(...)
    failed: int = Field(...)
    results: list[dict[str, Any]] = Field(...)
    errors: list[dict[str, Any]] = Field(default_factory=list)


# Permission check response
class PermissionCheckResponse(BaseResponse):
    success: bool = Field(True)
    user_role: str = Field(...)
    action: str = Field(...)
    allowed: bool = Field(...)
    reason: str | None = Field(None)


# Workflow status response
class WorkflowStatusResponse(BaseResponse):
    success: bool = Field(True)
    feature_name: str = Field(...)
    current_status: str = Field(...)
    allowed_transitions: list[str] = Field(...)
    workflow_history: list[dict[str, Any]] = Field(default_factory=list)


# Export response
class ExportResponse(BaseResponse):
    success: bool = Field(True)
    export_format: str = Field(...)
    data: Any = Field(...)
    metadata: dict[str, Any] = Field(default_factory=dict)


# Import response
class ImportResponse(BaseResponse):
    success: bool = Field(True)
    imported_count: int = Field(...)
    skipped_count: int = Field(default=0)
    error_count: int = Field(default=0)
    errors: list[dict[str, Any]] = Field(default_factory=list)


# Cache statistics response
class CacheStatsResponse(BaseResponse):
    success: bool = Field(True)
    cache_size: int = Field(...)
    hit_rate: float = Field(...)
    miss_rate: float = Field(...)
    total_requests: int = Field(...)
    cache_entries: dict[str, Any] = Field(default_factory=dict)


# System statistics response
class SystemStatsResponse(BaseResponse):
    success: bool = Field(True)
    memory_usage: dict[str, Any] = Field(...)
    cpu_usage: float = Field(...)
    disk_usage: dict[str, Any] = Field(...)
    active_connections: int = Field(...)
    request_stats: dict[str, Any] = Field(...)


# Configuration response
class ConfigResponse(BaseResponse):
    success: bool = Field(True)
    config: dict[str, Any] = Field(...)
    environment: str = Field(...)
    debug_mode: bool = Field(False)


# Log response
class LogResponse(BaseResponse):
    success: bool = Field(True)
    logs: list[dict[str, Any]] = Field(...)
    total_entries: int = Field(...)
    log_level: str = Field(...)
    time_range: dict[str, int] = Field(...)


# Backup response
class BackupResponse(BaseResponse):
    success: bool = Field(True)
    backup_id: str = Field(...)
    backup_size: int = Field(...)
    backup_path: str | None = Field(None)
    compressed: bool = Field(False)


# Restore response
class RestoreResponse(BaseResponse):
    success: bool = Field(True)
    backup_id: str = Field(...)
    restored_items: int = Field(...)
    restore_time_seconds: float = Field(...)
    validation_results: dict[str, Any] = Field(default_factory=dict)
