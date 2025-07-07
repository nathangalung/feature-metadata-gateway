from pydantic import BaseModel, Field, field_validator


class FeatureRequest(BaseModel):
    """Request model for feature metadata"""

    model_config = {
        "json_schema_extra": {
            "example": {
                "features": [
                    "driver_hourly_stats:conv_rate:1",
                    "driver_hourly_stats:acc_rate:2",
                    "driver_hourly_stats:avg_daily_trips:3",
                ],
                "entities": {"cust_no": ["X123456", "1002"]},
                "event_timestamp": 1751429485000,
            }
        }
    }

    features: list[str] = Field(..., description="Feature names with format category:name:version")
    entities: dict[str, list[str]] = Field(..., description="Entity identifiers")
    event_timestamp: int | None = Field(None, description="Event timestamp in ms (Unix GMT+0)")

    @field_validator("features", mode="before")
    @classmethod
    def validate_features(cls, v):
        if not isinstance(v, list):
            raise TypeError("features must be a list")
        return v

    @field_validator("entities", mode="before")
    @classmethod
    def validate_entities(cls, v):
        if not isinstance(v, dict):
            raise TypeError("entities must be a dictionary")
        if not v:
            raise ValueError("entities cannot be empty")
        return v
