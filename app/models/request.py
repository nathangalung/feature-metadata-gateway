import re
from typing import Any

from pydantic import BaseModel, Field, validator


# Feature metadata model
class FeatureMetadata(BaseModel):
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


# Get feature request model
class GetFeatureRequest(BaseModel):
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


# Get all features request model
class GetAllFeaturesRequest(BaseModel):
    status: str | None = None
    feature_type: str | None = None
    created_by: str | None = None
    limit: int | None = None
    offset: int | None = None
    user_role: str


# Create feature request model
class CreateFeatureRequest(BaseModel):
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


# Update feature request model
class UpdateFeatureRequest(BaseModel):
    feature_name: str
    feature_type: str | None = None
    feature_data_type: str | None = None
    query: str | None = None
    description: str | None = None
    status: str | None = None
    last_updated_by: str
    user_role: str


# Delete feature request model
class DeleteFeatureRequest(BaseModel):
    feature_name: str
    deleted_by: str
    user_role: str
    deletion_reason: str | None = None


# Ready for testing request model
class ReadyTestRequest(BaseModel):
    feature_name: str
    submitted_by: str
    user_role: str


# Alias for ready test request
class ReadyTestFeatureRequest(ReadyTestRequest):
    pass


# Test feature request model
class TestFeatureRequest(BaseModel):
    feature_name: str
    test_result: str
    tested_by: str
    test_notes: str | None = None
    user_role: str


# Fix feature request model
class FixFeatureRequest(BaseModel):
    feature_name: str
    fixed_by: str
    fix_description: str
    user_role: str


# Approve feature request model
class ApproveFeatureRequest(BaseModel):
    feature_name: str
    approved_by: str
    approval_notes: str | None = None
    user_role: str


# Reject feature request model
class RejectFeatureRequest(BaseModel):
    feature_name: str
    rejected_by: str
    rejection_reason: str
    user_role: str


# Batch feature result model
class BatchFeatureResult(BaseModel):
    values: list[Any]
    messages: list[str]
    event_timestamps: list[int]


# Batch feature request model
class BatchFeatureRequest(BaseModel):
    features: list[str]
    entities: dict[str, list[str]]
    event_timestamp: int | None = None


# Batch feature response model
class BatchFeatureResponse(BaseModel):
    metadata: dict[str, Any]
    results: list[BatchFeatureResult]
