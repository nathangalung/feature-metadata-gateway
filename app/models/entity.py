from typing import Any

from pydantic import BaseModel


# Feature metadata model
class FeatureMetadataEntity(BaseModel):
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


# Single metadata response
class FeatureMetadataSingleResponse(BaseModel):
    values: dict[str, Any]
    status: str
    event_timestamp: int


# Batch metadata response
class FeatureMetadataBatchResponse(BaseModel):
    metadata: dict[str, Any]
    results: dict[str, list[Any]]
