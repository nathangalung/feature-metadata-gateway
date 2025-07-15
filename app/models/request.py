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


# Get metadata request (single/multiple)
class GetFeatureMetadataRequest(BaseModel):
    features: str | list[str]
    user_role: str

    @validator("features")
    @classmethod
    def validate_features(cls, v: str | list[str]) -> str | list[str]:
        if isinstance(v, str):
            if not v.strip():
                raise ValueError("features cannot be empty")
        elif isinstance(v, list):
            if not v or not all(isinstance(i, str) and i.strip() for i in v):
                raise ValueError("features list cannot be empty")
        else:
            raise ValueError("features must be str or list of str")
        return v

    @validator("user_role")
    def validate_user_role(cls, v: str) -> str:
        if not v or not isinstance(v, str) or v.strip() == "":
            raise ValueError("User role cannot be empty")
        return v


# Create metadata request
class CreateFeatureMetadataRequest(BaseModel):
    feature_name: str = Field(..., min_length=1)
    feature_type: str = Field(..., min_length=1)
    feature_data_type: str = Field(..., min_length=1)
    query: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    created_by: str = Field(..., min_length=1)
    user_role: str = Field(..., min_length=1)


# Update metadata request
class UpdateFeatureMetadataRequest(BaseModel):
    feature_name: str
    feature_type: str | None = None
    feature_data_type: str | None = None
    query: str | None = None
    description: str | None = None
    last_updated_by: str
    user_role: str


# Delete metadata request
class DeleteFeatureMetadataRequest(BaseModel):
    feature_name: str
    deleted_by: str
    user_role: str
    deletion_reason: str


# Submit for testing request
class SubmitTestFeatureMetadataRequest(BaseModel):
    feature_name: str
    submitted_by: str
    user_role: str


# Test metadata request
class TestFeatureMetadataRequest(BaseModel):
    feature_name: str
    test_result: str
    tested_by: str
    test_notes: str | None = None
    user_role: str


# Approve metadata request
class ApproveFeatureMetadataRequest(BaseModel):
    feature_name: str
    approved_by: str
    approval_notes: str | None = None
    user_role: str


# Reject metadata request
class RejectFeatureMetadataRequest(BaseModel):
    feature_name: str
    rejected_by: str
    rejection_reason: str
    user_role: str
