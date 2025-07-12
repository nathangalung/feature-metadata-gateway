"""Entity models."""

from typing import Any

from pydantic import BaseModel


class Entity(BaseModel):
    """Entity data."""

    entity_id: str
    entity_type: str
    created_time: int | None = None
    updated_time: int | None = None


class EntityRequest(BaseModel):
    """Entity request."""

    entity_id: str
    entity_type: str


class EntityResponse(BaseModel):
    """Entity response."""

    entity: Entity
    success: bool = True
    event_timestamp: int


class BatchEntityRequest(BaseModel):
    """Batch entity request."""

    entities: list[EntityRequest]


class BatchEntityResponse(BaseModel):
    """Batch entity response."""

    entities: list[Entity]
    count: int
    success: bool = True
    event_timestamp: int


# Feature value model for batch/dummy
class FeatureValue(BaseModel):
    """Feature value."""

    feature_type: str
    feature_data_type: str
    query: str
    created_time: int
    updated_time: int
    deleted_time: int | None = None
    created_by: str
    last_updated_by: str | None = None
    deleted_by: str | None = None
    approved_by: str | None = None
    status: str
    description: str


class FeatureResult(BaseModel):
    """Feature result."""

    values: list[Any]
    messages: list[str]
    event_timestamps: list[int]


class FeatureMetadataResponse(BaseModel):
    """Feature metadata response."""

    metadata: dict[str, Any]
    results: FeatureResult


class FeatureEntity(BaseModel):
    features: list[str]
    entities: dict[str, list[str]]
    event_timestamp: int | None = None


class BatchFeatureRequest(BaseModel):
    features: list[str]
    entities: dict[str, list[str]]
    event_timestamp: int | None = None


class BatchFeatureResponse(BaseModel):
    results: list[FeatureValue]
