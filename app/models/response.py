from typing import Any

from pydantic import BaseModel, Field


class FeatureValue(BaseModel):
    """Individual feature value with metadata"""

    value: float | int | str = Field(..., description="Feature value")
    feature_type: str = Field(..., description="real-time or batch")
    feature_data_type: str = Field(..., description="Data type of feature")
    query: str = Field(..., description="SQL query for feature")
    created_time: int = Field(..., description="Creation timestamp (Unix GMT+0 ms)")
    updated_time: int = Field(..., description="Last update timestamp (Unix GMT+0 ms)")
    created_by: str = Field(..., description="Creator username")
    last_updated_by: str = Field(..., description="Last updater username")
    approved_by: str | None = Field(None, description="Approver username")
    status: str | None = Field(None, description="Feature status")
    description: str | None = Field(None, description="Feature description")
    event_timestamp: int = Field(..., description="Event timestamp (Unix GMT+0 ms)")


class EntityResult(BaseModel):
    """Results for a single entity"""

    values: list[str | FeatureValue] = Field(..., description="Entity ID and feature values")
    statuses: list[str] = Field(..., description="Status codes for each feature")
    event_timestamps: list[int] = Field(..., description="Event timestamps for each feature")


class FeatureResponse(BaseModel):
    """Feature metadata response"""

    metadata: dict[str, Any] = Field(..., description="Request metadata")
    results: list[EntityResult] = Field(..., description="Results for each entity")
