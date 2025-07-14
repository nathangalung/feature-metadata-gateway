from typing import Any

from pydantic import BaseModel


# Entity data model
class Entity(BaseModel):
    entity_id: str
    entity_type: str
    created_time: int | None = None
    updated_time: int | None = None


# Entity request model
class EntityRequest(BaseModel):
    entity_id: str
    entity_type: str


# Entity response model
class EntityResponse(BaseModel):
    entity: Entity
    success: bool = True
    event_timestamp: int


# Batch entity request model
class BatchEntityRequest(BaseModel):
    entities: list[EntityRequest]


# Batch entity response model
class BatchEntityResponse(BaseModel):
    entities: list[Entity]
    count: int
    success: bool = True
    event_timestamp: int


# Feature value model
class FeatureValue(BaseModel):
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


# Feature result model
class FeatureResult(BaseModel):
    values: list[Any]
    messages: list[str]
    event_timestamps: list[int]


# Feature metadata response model
class FeatureMetadataResponse(BaseModel):
    metadata: dict[str, Any]
    results: FeatureResult


# Feature entity model
class FeatureEntity(BaseModel):
    features: list[str]
    entities: dict[str, list[str]]
    event_timestamp: int | None = None


# Batch feature request model
class BatchFeatureRequest(BaseModel):
    features: list[str]
    entities: dict[str, list[str]]
    event_timestamp: int | None = None


# Batch feature response model
class BatchFeatureResponse(BaseModel):
    results: list[FeatureValue]
