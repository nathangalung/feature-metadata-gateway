"""Response models for the API."""

from typing import Any

from pydantic import BaseModel, Field, validator

from app.models.request import FeatureMetadata
from app.utils.timestamp import get_current_timestamp


class BaseResponse(BaseModel):
    """Base response model."""

    timestamp: int = Field(
        default_factory=get_current_timestamp, description="Response timestamp"
    )
    request_id: str | None = Field(None, description="Request identifier")


class SuccessResponse(BaseResponse):
    """Generic success response."""

    success: bool = Field(True, description="Success indicator")
    message: str = Field(..., description="Success message")
    data: Any | None = Field(None, description="Response data")


class ErrorResponse(BaseResponse):
    """Error response model."""

    success: bool = Field(False, description="Success indicator")
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: dict[str, Any] | None = Field(None, description="Error details")


class FeatureMetadataResponse(BaseResponse):
    """Response for single feature metadata."""

    success: bool = Field(True, description="Success indicator")
    metadata: FeatureMetadata = Field(..., description="Feature metadata")


class AllMetadataResponse(BaseResponse):
    """Response for all feature metadata."""

    success: bool = Field(True, description="Success indicator")
    metadata: dict[str, FeatureMetadata] | list[FeatureMetadata] = Field(
        ..., description="All feature metadata"
    )
    total_count: int = Field(..., description="Total number of features")

    def __init__(self, **data):
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
    def validate_metadata(cls, v):
        if isinstance(v, dict):
            return list(v.values())
        return v if v is not None else []


class FilteredMetadataResponse(BaseResponse):
    """Response for filtered feature metadata."""

    success: bool = Field(True, description="Success indicator")
    metadata: list[FeatureMetadata] = Field(
        ..., description="Filtered feature metadata"
    )
    total_count: int = Field(..., description="Total number of matching features")
    filters_applied: dict[str, Any] = Field(..., description="Applied filters")


class CreateFeatureResponse(BaseResponse):
    """Response for feature creation."""

    success: bool = Field(True, description="Success indicator")
    message: str = Field("Feature created successfully", description="Success message")
    metadata: FeatureMetadata = Field(..., description="Created feature metadata")


class UpdateFeatureResponse(BaseResponse):
    """Response for feature update."""

    success: bool = Field(True, description="Success indicator")
    message: str = Field("Feature updated successfully", description="Success message")
    metadata: FeatureMetadata = Field(..., description="Updated feature metadata")


class DeleteFeatureResponse(BaseResponse):
    """Response for feature deletion."""

    success: bool = Field(True, description="Success indicator")
    message: str = Field("Feature deleted successfully", description="Success message")
    metadata: FeatureMetadata = Field(..., description="Deleted feature metadata")


class WorkflowResponse(BaseResponse):
    """Response for workflow operations."""

    success: bool = Field(True, description="Success indicator")
    message: str = Field(..., description="Workflow operation message")
    metadata: FeatureMetadata = Field(..., description="Updated feature metadata")
    previous_status: str = Field(..., description="Previous feature status")
    new_status: str = Field(..., description="New feature status")


class ReadyTestResponse(WorkflowResponse):
    """Response for ready test operation."""

    message: str = Field("Feature submitted for testing", description="Success message")


class TestFeatureResponse(WorkflowResponse):
    """Response for test feature operation."""

    test_result: str = Field(..., description="Test result")
    test_notes: str | None = Field(None, description="Test notes")


class ApproveFeatureResponse(WorkflowResponse):
    """Response for approve feature operation."""

    message: str = Field("Feature approved and deployed", description="Success message")
    approved_by: str = Field(..., description="Approver identifier")


class RejectFeatureResponse(WorkflowResponse):
    """Response for reject feature operation."""

    message: str = Field("Feature rejected", description="Success message")
    rejection_reason: str = Field(..., description="Rejection reason")


class FixFeatureResponse(WorkflowResponse):
    """Response for fix feature operation."""

    message: str = Field(
        "Feature fixed and reset to DRAFT", description="Success message"
    )
    fix_description: str = Field(..., description="Fix description")


class HealthResponse(BaseResponse):
    """Health check response."""

    status: str = Field("healthy", description="Health status")
    version: str = Field("1.0.0", description="API version")
    uptime_seconds: int = Field(0, description="Service uptime")
    dependencies: dict[str, str] = Field(
        default_factory=dict, description="Dependency status"
    )


class ValidationResponse(BaseResponse):
    """Validation response."""

    is_valid: bool = Field(..., description="Validation result")
    errors: list[str] = Field(default_factory=list, description="Validation errors")
    warnings: list[str] = Field(default_factory=list, description="Validation warnings")


class StatusListResponse(BaseResponse):
    """Response for status-based feature lists."""

    success: bool = Field(True, description="Success indicator")
    status: str = Field(..., description="Status filter")
    features: list[str] = Field(..., description="List of feature names")
    count: int = Field(..., description="Number of features")

    def __init__(self, **data):
        if "count" not in data and "features" in data:
            data["count"] = len(data["features"])
        super().__init__(**data)


class DeployedFeaturesResponse(StatusListResponse):
    """Response for deployed features list."""

    status: str = Field("DEPLOYED", description="Status filter")


class FeatureStatsResponse(BaseResponse):
    """Response for feature statistics."""

    success: bool = Field(True, description="Success indicator")
    total_features: int = Field(..., description="Total number of features")
    features_by_status: dict[str, int] = Field(
        ..., description="Feature count by status"
    )
    features_by_type: dict[str, int] = Field(..., description="Feature count by type")
    features_by_data_type: dict[str, int] = Field(
        ..., description="Feature count by data type"
    )
    recent_activity: list[dict[str, Any]] = Field(
        default_factory=list, description="Recent feature activity"
    )


class BulkOperationResponse(BaseResponse):
    """Response for bulk operations."""

    success: bool = Field(True, description="Overall success indicator")
    total_requested: int = Field(..., description="Total operations requested")
    successful: int = Field(..., description="Number of successful operations")
    failed: int = Field(..., description="Number of failed operations")
    results: list[dict[str, Any]] = Field(
        ..., description="Individual operation results"
    )
    errors: list[dict[str, Any]] = Field(
        default_factory=list, description="Operation errors"
    )


class PermissionCheckResponse(BaseResponse):
    """Response for permission checks."""

    success: bool = Field(True, description="Success indicator")
    user_role: str = Field(..., description="User role")
    action: str = Field(..., description="Requested action")
    allowed: bool = Field(..., description="Whether action is allowed")
    reason: str | None = Field(None, description="Reason if not allowed")


class WorkflowStatusResponse(BaseResponse):
    """Response for workflow status information."""

    success: bool = Field(True, description="Success indicator")
    feature_name: str = Field(..., description="Feature name")
    current_status: str = Field(..., description="Current status")
    allowed_transitions: list[str] = Field(
        ..., description="Allowed status transitions"
    )
    workflow_history: list[dict[str, Any]] = Field(
        default_factory=list, description="Workflow history"
    )


class ExportResponse(BaseResponse):
    """Response for data export operations."""

    success: bool = Field(True, description="Success indicator")
    export_format: str = Field(..., description="Export format")
    data: Any = Field(..., description="Exported data")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Export metadata"
    )


class ImportResponse(BaseResponse):
    """Response for data import operations."""

    success: bool = Field(True, description="Success indicator")
    imported_count: int = Field(..., description="Number of imported items")
    skipped_count: int = Field(default=0, description="Number of skipped items")
    error_count: int = Field(default=0, description="Number of errors")
    errors: list[dict[str, Any]] = Field(
        default_factory=list, description="Import errors"
    )


class CacheStatsResponse(BaseResponse):
    """Response for cache statistics."""

    success: bool = Field(True, description="Success indicator")
    cache_size: int = Field(..., description="Current cache size")
    hit_rate: float = Field(..., description="Cache hit rate")
    miss_rate: float = Field(..., description="Cache miss rate")
    total_requests: int = Field(..., description="Total cache requests")
    cache_entries: dict[str, Any] = Field(
        default_factory=dict, description="Cache entries info"
    )


class SystemStatsResponse(BaseResponse):
    """Response for system statistics."""

    success: bool = Field(True, description="Success indicator")
    memory_usage: dict[str, Any] = Field(..., description="Memory usage statistics")
    cpu_usage: float = Field(..., description="CPU usage percentage")
    disk_usage: dict[str, Any] = Field(..., description="Disk usage statistics")
    active_connections: int = Field(..., description="Number of active connections")
    request_stats: dict[str, Any] = Field(..., description="Request statistics")


class ConfigResponse(BaseResponse):
    """Response for configuration information."""

    success: bool = Field(True, description="Success indicator")
    config: dict[str, Any] = Field(..., description="Configuration settings")
    environment: str = Field(..., description="Environment name")
    debug_mode: bool = Field(False, description="Debug mode status")


class LogResponse(BaseResponse):
    """Response for log information."""

    success: bool = Field(True, description="Success indicator")
    logs: list[dict[str, Any]] = Field(..., description="Log entries")
    total_entries: int = Field(..., description="Total number of log entries")
    log_level: str = Field(..., description="Log level filter")
    time_range: dict[str, int] = Field(..., description="Time range for logs")


class BackupResponse(BaseResponse):
    """Response for backup operations."""

    success: bool = Field(True, description="Success indicator")
    backup_id: str = Field(..., description="Backup identifier")
    backup_size: int = Field(..., description="Backup size in bytes")
    backup_path: str | None = Field(None, description="Backup file path")
    compressed: bool = Field(False, description="Whether backup is compressed")


class RestoreResponse(BaseResponse):
    """Response for restore operations."""

    success: bool = Field(True, description="Success indicator")
    backup_id: str = Field(..., description="Restored backup identifier")
    restored_items: int = Field(..., description="Number of restored items")
    restore_time_seconds: float = Field(..., description="Time taken for restore")
    validation_results: dict[str, Any] = Field(
        default_factory=dict, description="Post-restore validation"
    )
