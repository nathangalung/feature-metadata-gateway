from typing import Any

from pydantic import BaseModel, Field

from app.models.request import FeatureMetadata
from app.utils.timestamp import get_current_timestamp


# Base response
class BaseResponse(BaseModel):
    timestamp: int = Field(default_factory=get_current_timestamp)
    request_id: str | None = Field(None)


# Single metadata response
class FeatureMetadataSingleResponse(BaseModel):
    values: dict[str, Any]
    status: str
    event_timestamp: int


# Batch metadata response
class FeatureMetadataBatchResponse(BaseModel):
    metadata: dict[str, Any]
    results: dict[str, Any]


# Create response
class CreateFeatureMetadataResponse(BaseResponse):
    success: bool = Field(True)
    message: str = Field("Feature metadata created successfully")
    metadata: FeatureMetadata = Field(...)


# Update response
class UpdateFeatureMetadataResponse(BaseResponse):
    success: bool = Field(True)
    message: str = Field("Feature metadata updated successfully")
    metadata: FeatureMetadata = Field(...)


# Delete response
class DeleteFeatureMetadataResponse(BaseResponse):
    success: bool = Field(True)
    message: str = Field("Feature metadata deleted successfully")
    metadata: FeatureMetadata = Field(...)


# Workflow response
class WorkflowMetadataResponse(BaseResponse):
    success: bool = Field(True)
    message: str = Field(...)
    metadata: FeatureMetadata = Field(...)
    previous_status: str = Field(...)
    new_status: str = Field(...)


# Health check response
class HealthResponse(BaseResponse):
    status: str = Field("healthy")
    version: str = Field("1.0.0")
    uptime_seconds: int = Field(0)
    dependencies: dict[str, str] = Field(default_factory=dict)
