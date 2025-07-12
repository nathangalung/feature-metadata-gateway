"""Feature metadata models."""

import re
from typing import Any

from pydantic import BaseModel, Field, validator


class FeatureMetadata(BaseModel):
    """Feature metadata model."""

    feature_name: str
    feature_type: str
    feature_data_type: str
    query: str
    description: str
    status: str
    created_time: int
    updated_time: int
    created_by: str
    last_updated_by: str | None = None
    submitted_by: str | None = None
    tested_by: str | None = None
    tested_time: int | None = None
    test_result: str | None = None
    test_notes: str | None = None
    approved_by: str | None = None
    approved_time: int | None = None
    approval_notes: str | None = None
    rejected_by: str | None = None
    rejection_reason: str | None = None
    deployed_by: str | None = None
    deployed_time: int | None = None
    deleted_by: str | None = None
    deleted_time: int | None = None
    deletion_reason: str | None = None
    fixed_by: str | None = None
    fix_description: str | None = None

    class Config:
        arbitrary_types_allowed = True


class GetFeatureRequest(BaseModel):
    """Get feature metadata request model."""

    feature_name: str
    user_role: str

    @validator("feature_name")
    def validate_feature_name(cls, v: str) -> str:
        if not v or not isinstance(v, str) or v.strip() == "":
            raise ValueError("Feature name cannot be empty")
        if not re.match(r"^[a-zA-Z0-9_-]+:[a-zA-Z0-9_-]+:v\d+$", v):
            raise ValueError("Invalid feature name format")
        return v

    @validator("user_role")
    def validate_user_role(cls, v: str) -> str:
        if not v or not isinstance(v, str) or v.strip() == "":
            raise ValueError("User role cannot be empty")
        return v


class GetAllFeaturesRequest(BaseModel):
    """Get all features request model."""

    status: str | None = None
    feature_type: str | None = None
    created_by: str | None = None
    limit: int | None = None
    offset: int | None = None
    user_role: str


class CreateFeatureRequest(BaseModel):
    """Create feature request model."""

    feature_name: str = Field(..., min_length=1)
    feature_type: str = Field(..., min_length=1)
    feature_data_type: str = Field(..., min_length=1)
    query: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    created_by: str = Field(..., min_length=1)
    user_role: str = Field(..., min_length=1)

    @validator("feature_name")
    def validate_feature_name(cls, v: str) -> str:
        if not v or not isinstance(v, str) or v.strip() == "":
            raise ValueError("feature_name cannot be empty")
        return v.strip()

    @validator("created_by")
    def validate_created_by(cls, v: str) -> str:
        if not v or not isinstance(v, str) or v.strip() == "":
            raise ValueError("created_by cannot be empty")
        return v.strip()

    @validator("description")
    def validate_description(cls, v: str) -> str:
        if not v or not isinstance(v, str) or v.strip() == "":
            raise ValueError("description cannot be empty")
        return v.strip()

    @validator("query")
    def validate_query(cls, v: str) -> str:
        if not v or not isinstance(v, str) or v.strip() == "":
            raise ValueError("query cannot be empty")
        return v.strip()


class UpdateFeatureRequest(BaseModel):
    """Update feature request model."""

    feature_name: str
    feature_type: str | None = None
    feature_data_type: str | None = None
    query: str | None = None
    description: str | None = None
    status: str | None = None
    last_updated_by: str
    user_role: str


class DeleteFeatureRequest(BaseModel):
    feature_name: str
    deleted_by: str
    user_role: str
    deletion_reason: str | None = None


class ReadyTestRequest(BaseModel):
    """Ready for testing request model."""

    feature_name: str
    submitted_by: str
    user_role: str


class ReadyTestFeatureRequest(ReadyTestRequest):
    """Alias for ReadyTestRequest for backward compatibility."""

    pass


class TestFeatureRequest(BaseModel):
    """Test feature request model."""

    feature_name: str
    test_result: str
    tested_by: str
    test_notes: str | None = None
    user_role: str


class FixFeatureRequest(BaseModel):
    """Fix feature request model."""

    feature_name: str
    fixed_by: str
    fix_description: str
    user_role: str


class ApproveFeatureRequest(BaseModel):
    """Approve feature request model."""

    feature_name: str
    approved_by: str
    approval_notes: str | None = None
    user_role: str


class RejectFeatureRequest(BaseModel):
    """Reject feature request model."""

    feature_name: str
    rejected_by: str
    rejection_reason: str
    user_role: str


class BatchFeatureResult(BaseModel):
    """Batch feature result."""

    values: list[Any]
    messages: list[str]
    event_timestamps: list[int]


class BatchFeatureRequest(BaseModel):
    """Batch feature request model."""

    features: list[str]
    entities: dict[str, list[str]]
    event_timestamp: int | None = None


class BatchFeatureResponse(BaseModel):
    """Batch feature response."""

    metadata: dict[str, Any]
    results: list[BatchFeatureResult]
