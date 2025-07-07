from typing import Any

from pydantic import BaseModel, Field


class FeatureValue(BaseModel):
    """Feature value with metadata"""

    value: Any = Field(..., description="Feature value")
    feature_type: str = Field(..., description="Feature type (real-time/batch)")
    feature_data_type: str = Field(..., description="Data type (float/integer/string)")
    query: str = Field(..., description="SQL query for feature")
    created_time: int = Field(..., description="Creation timestamp in ms")
    updated_time: int = Field(..., description="Last update timestamp in ms")
    created_by: str = Field(..., description="Creator name")
    last_updated_by: str = Field(..., description="Last updater name")
    approved_by: str | None = Field(None, description="Approver name")
    status: str | None = Field(None, description="Feature status")
    description: str | None = Field(None, description="Feature description")
    event_timestamp: int = Field(..., description="Event timestamp in ms")


class EntityResult(BaseModel):
    """Results for single entity"""

    values: list[str | FeatureValue] = Field(..., description="Entity ID and feature values")
    statuses: list[str] = Field(..., description="Status codes for each feature")
    event_timestamps: list[int] = Field(..., description="Event timestamps for each feature")


class FeatureResponse(BaseModel):
    """Feature metadata response"""

    metadata: dict[str, Any] = Field(..., description="Request metadata")
    results: list[EntityResult] = Field(..., description="Results for each entity")
