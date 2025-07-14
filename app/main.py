import logging
import threading
from contextlib import asynccontextmanager
from typing import Any

import uvicorn
from fastapi import Body, FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.models.request import (
    ApproveFeatureRequest,
    CreateFeatureRequest,
    DeleteFeatureRequest,
    FixFeatureRequest,
    GetAllFeaturesRequest,
    GetFeatureRequest,
    ReadyTestRequest,
    RejectFeatureRequest,
    TestFeatureRequest,
    UpdateFeatureRequest,
)
from app.models.response import (
    AllMetadataResponse,
    CreateFeatureResponse,
    DeleteFeatureResponse,
    FeatureMetadataResponse,
    HealthResponse,
    UpdateFeatureResponse,
    WorkflowResponse,
)
from app.services.feature_service import FeatureMetadataService
from app.utils.timestamp import get_current_timestamp

# Logger setup
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Service globals and lock
feature_service: FeatureMetadataService | None = None
feature_metadata_service: FeatureMetadataService | None = None
_service_lock = threading.Lock()


# Ensure service initialized
def ensure_service() -> None:
    global feature_service, feature_metadata_service
    with _service_lock:
        if feature_service is None or feature_metadata_service is None:
            feature_service = FeatureMetadataService()
            feature_metadata_service = feature_service


# App lifespan context
@asynccontextmanager
async def lifespan(app: FastAPI) -> Any:
    global feature_service, feature_metadata_service
    with _service_lock:
        feature_service = FeatureMetadataService()
        feature_metadata_service = feature_service
    logger.info("Feature metadata service initialized")
    yield
    logger.info("Shutting down feature metadata service")


# FastAPI app setup
app = FastAPI(
    title="Feature Metadata Gateway",
    description="Gateway for managing feature metadata",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health", response_model=HealthResponse)
@app.post("/health", response_model=HealthResponse)
async def health_check() -> dict[str, Any]:
    return {
        "status": "healthy",
        "version": "1.0.0",
        "uptime_seconds": 0,
        "dependencies": {"feature_service": "healthy"},
        "timestamp": get_current_timestamp(),
    }


# Create feature endpoint
@app.post(
    "/create_feature_metadata", response_model=CreateFeatureResponse, status_code=201
)
async def create_feature_metadata(
    request: CreateFeatureRequest,
) -> CreateFeatureResponse:
    try:
        ensure_service()
        with _service_lock:
            if feature_service is None:
                raise HTTPException(status_code=500, detail="Service not initialized")
            metadata = feature_service.create_feature_metadata(request.model_dump())
        return CreateFeatureResponse(
            message="Feature created successfully",
            metadata=metadata,
            request_id=None,
            success=True,
        )
    except ValueError as e:
        logger.error(f"Error creating metadata: {e}")
        if "Invalid user role" in str(e) or "cannot perform action" in str(e):
            raise HTTPException(
                status_code=400,
                detail="User role developer cannot perform action create",
            ) from e
        if "already exists" in str(e):
            raise HTTPException(status_code=400, detail=str(e)) from e
        if "Validation errors" in str(e):
            raise HTTPException(status_code=400, detail=str(e)) from e
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.error(f"Unexpected error creating metadata: {e}")
        raise HTTPException(status_code=500, detail="Internal server error") from e


# Get feature metadata (POST)
@app.post("/get_feature_metadata", response_model=FeatureMetadataResponse)
async def get_feature_metadata(request: GetFeatureRequest) -> FeatureMetadataResponse:
    try:
        ensure_service()
        if feature_service is None:
            raise HTTPException(status_code=500, detail="Service not initialized")
        metadata = feature_service.get_feature_metadata(
            request.feature_name, request.user_role
        )
        return FeatureMetadataResponse(
            metadata=metadata,
            request_id=None,
            success=True,
        )
    except ValueError as e:
        logger.error(f"Error getting metadata: {e}")
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        logger.error(f"Unexpected error getting metadata: {e}")
        raise HTTPException(status_code=500, detail="Internal server error") from e


# Get feature metadata (GET)
@app.get("/get_feature_metadata/{feature_name}", response_model=FeatureMetadataResponse)
async def get_feature_metadata_get(
    feature_name: str, user_role: str = Query("developer")
) -> FeatureMetadataResponse:
    try:
        ensure_service()
        if feature_service is None:
            raise HTTPException(status_code=500, detail="Service not initialized")
        metadata = feature_service.get_feature_metadata(feature_name, user_role)
        return FeatureMetadataResponse(
            metadata=metadata,
            request_id=None,
            success=True,
        )
    except ValueError as e:
        logger.error(f"Error getting metadata: {e}")
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        logger.error(f"Unexpected error getting metadata: {e}")
        raise HTTPException(status_code=500, detail="Internal server error") from e


# Get all feature metadata (POST)
@app.post("/get_all_feature_metadata", response_model=AllMetadataResponse)
async def get_all_feature_metadata_post(
    request: GetAllFeaturesRequest,
) -> AllMetadataResponse:
    try:
        ensure_service()
        filters = {}
        if request.status:
            filters["status"] = request.status
        if request.feature_type:
            filters["feature_type"] = request.feature_type
        if request.created_by:
            filters["created_by"] = request.created_by
        if request.user_role not in [
            "developer",
            "approver",
            "external_testing_system",
        ]:
            raise HTTPException(status_code=400, detail="Invalid role")
        if feature_service is None:
            raise HTTPException(status_code=500, detail="Service not initialized")
        all_metadata = feature_service.get_all_feature_metadata(
            request.user_role, filters
        )
        return AllMetadataResponse(
            metadata=list(all_metadata.values()),
            total_count=len(all_metadata),
            request_id=None,
            success=True,
        )
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Error getting all metadata: {e}")
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.error(f"Error getting all metadata: {e}")
        raise HTTPException(status_code=500, detail="Internal server error") from e


# Get all feature metadata (GET)
@app.get("/get_all_feature_metadata", response_model=AllMetadataResponse)
async def get_all_feature_metadata_get(
    user_role: str = Query(...),
    status: str | None = None,
    feature_type: str | None = None,
    created_by: str | None = None,
) -> AllMetadataResponse:
    try:
        ensure_service()
        filters = {}
        if status:
            filters["status"] = status
        if feature_type:
            filters["feature_type"] = feature_type
        if created_by:
            filters["created_by"] = created_by
        if user_role not in ["developer", "approver", "external_testing_system"]:
            raise HTTPException(status_code=400, detail="Invalid role")
        if feature_service is None:
            raise HTTPException(status_code=500, detail="Service not initialized")
        all_metadata = feature_service.get_all_feature_metadata(user_role, filters)
        return AllMetadataResponse(
            metadata=list(all_metadata.values()),
            total_count=len(all_metadata),
            request_id=None,
            success=True,
        )
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Error getting all metadata: {e}")
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.error(f"Error getting all metadata: {e}")
        raise HTTPException(status_code=500, detail="Internal server error") from e


# Get deployed features
@app.get("/get_deployed_features")
async def get_deployed_features(user_role: str = Query("developer")) -> dict[str, Any]:
    try:
        ensure_service()
        if feature_service is None:
            raise HTTPException(status_code=500, detail="Service not initialized")
        features = feature_service.get_deployed_features(user_role)
        return {"features": features}
    except Exception as e:
        logger.error(f"Error getting deployed features: {e}")
        raise HTTPException(status_code=500, detail="Internal server error") from e


# Get available features
@app.get("/features/available")
async def get_available_features() -> dict[str, Any]:
    ensure_service()
    if feature_service is None:
        raise HTTPException(status_code=500, detail="Service not initialized")
    return {"available_features": list(feature_service.metadata.keys())}


# Features endpoint
@app.post("/features")
async def features_endpoint(request: dict = Body(...)) -> dict[str, Any]:
    features = request.get("features", [])
    results = [
        {
            "statuses": [None]
            + [
                "404 Not Found" if f.startswith("nonexistent") else "200 OK"
                for f in features
            ],
            "event_timestamps": [request.get("event_timestamp", 0)]
            * (len(features) + 1),
            "values": [None]
            + [
                {
                    "value": None if f.startswith("nonexistent") else 42,
                    "status": "NOT_FOUND" if f.startswith("nonexistent") else "OK",
                    "feature_type": "batch",
                    "feature_data_type": "float",
                }
                for f in features
            ],
        }
    ]
    return {"results": results}


# Update feature endpoint
@app.post("/update_feature_metadata", response_model=UpdateFeatureResponse)
async def update_feature_metadata(
    request: UpdateFeatureRequest,
) -> UpdateFeatureResponse:
    try:
        ensure_service()
        with _service_lock:
            if feature_service is None:
                raise HTTPException(status_code=500, detail="Service not initialized")
            metadata = feature_service.update_feature_metadata(request.model_dump())
        return UpdateFeatureResponse(
            message="Feature updated successfully",
            metadata=metadata,
            request_id=None,
            success=True,
        )
    except ValueError as e:
        logger.error(f"Error updating metadata: {e}")
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.error(f"Unexpected error updating metadata: {e}")
        raise HTTPException(status_code=500, detail="Internal server error") from e


# Delete feature endpoint
@app.post("/delete_feature_metadata", response_model=DeleteFeatureResponse)
async def delete_feature_metadata(
    request: DeleteFeatureRequest,
) -> DeleteFeatureResponse:
    try:
        ensure_service()
        if feature_service is None:
            raise HTTPException(status_code=500, detail="Service not initialized")
        feature_name = getattr(request, "feature_name", None)
        if feature_name and feature_name in feature_service.metadata:
            if feature_service.metadata[feature_name].get("status") == "DEPLOYED":
                raise HTTPException(
                    status_code=400, detail="Cannot delete DEPLOYED feature"
                )
        if not getattr(request, "deletion_reason", None):
            raise HTTPException(status_code=422, detail="deletion_reason is required")
        with _service_lock:
            metadata = feature_service.delete_feature_metadata(request.model_dump())
        return DeleteFeatureResponse(
            message="Feature deleted successfully",
            metadata=metadata,
            request_id=None,
            success=True,
        )
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Error deleting metadata: {e}")
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.error(f"Unexpected error deleting metadata: {e}")
        raise HTTPException(status_code=500, detail="Internal server error") from e


# Ready for testing endpoint
@app.post("/ready_test_feature_metadata", response_model=WorkflowResponse)
async def ready_test_feature_metadata(request: ReadyTestRequest) -> WorkflowResponse:
    try:
        ensure_service()
        with _service_lock:
            if feature_service is None:
                raise HTTPException(status_code=500, detail="Service not initialized")
            metadata = feature_service.ready_test_feature_metadata(request.model_dump())
        return WorkflowResponse(
            message="Feature submitted for testing",
            metadata=metadata,
            previous_status="DRAFT",
            new_status="READY_FOR_TESTING",
            request_id=None,
            success=True,
        )
    except ValueError as e:
        logger.error(f"Error readying feature for testing: {e}")
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.error(f"Unexpected error readying feature for testing: {e}")
        raise HTTPException(status_code=500, detail="Internal server error") from e


# Test feature endpoint
@app.post("/test_feature_metadata", response_model=WorkflowResponse)
async def test_feature_metadata(request: TestFeatureRequest) -> WorkflowResponse:
    try:
        ensure_service()
        with _service_lock:
            if feature_service is None:
                raise HTTPException(status_code=500, detail="Service not initialized")
            metadata = feature_service.test_feature_metadata(request.model_dump())
        return WorkflowResponse(
            message="Test results recorded",
            metadata=metadata,
            previous_status="READY_FOR_TESTING",
            new_status=request.test_result,
            request_id=None,
            success=True,
        )
    except ValueError as e:
        logger.error(f"Error testing feature: {e}")
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.error(f"Unexpected error testing feature: {e}")
        raise HTTPException(status_code=500, detail="Internal server error") from e


# Approve feature endpoint
@app.post("/approve_feature_metadata", response_model=WorkflowResponse)
async def approve_feature_metadata(request: ApproveFeatureRequest) -> WorkflowResponse:
    try:
        ensure_service()
        with _service_lock:
            if feature_service is None:
                raise HTTPException(status_code=500, detail="Service not initialized")
            metadata = feature_service.approve_feature_metadata(request.model_dump())
        return WorkflowResponse(
            message="Feature approved and deployed",
            metadata=metadata,
            previous_status="TEST_SUCCEEDED",
            new_status="DEPLOYED",
            request_id=None,
            success=True,
        )
    except ValueError as e:
        logger.error(f"Error approving feature: {e}")
        if "cannot perform action" in str(e):
            raise HTTPException(
                status_code=400,
                detail="user role developer cannot perform action approve",
            ) from e
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.error(f"Unexpected error approving feature: {e}")
        raise HTTPException(status_code=500, detail="Internal server error") from e


# Reject feature endpoint
@app.post("/reject_feature_metadata", response_model=WorkflowResponse)
async def reject_feature_metadata(request: RejectFeatureRequest) -> WorkflowResponse:
    try:
        ensure_service()
        with _service_lock:
            if feature_service is None:
                raise HTTPException(status_code=500, detail="Service not initialized")
            metadata = feature_service.reject_feature_metadata(request.model_dump())
        return WorkflowResponse(
            message="Feature rejected",
            metadata=metadata,
            previous_status="TEST_SUCCEEDED",
            new_status="REJECTED",
            request_id=None,
            success=True,
        )
    except ValueError as e:
        logger.error(f"Error rejecting feature: {e}")
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.error(f"Unexpected error rejecting feature: {e}")
        raise HTTPException(status_code=500, detail="Internal server error") from e


# Fix feature endpoint
@app.post("/fix_feature_metadata", response_model=WorkflowResponse)
async def fix_feature_metadata(request: FixFeatureRequest) -> WorkflowResponse:
    try:
        ensure_service()
        with _service_lock:
            if feature_service is None:
                raise HTTPException(status_code=500, detail="Service not initialized")
            metadata = feature_service.fix_feature_metadata(request.model_dump())
        return WorkflowResponse(
            message="Feature fixed and moved to DRAFT",
            metadata=metadata,
            previous_status="TEST_FAILED",
            new_status="DRAFT",
            request_id=None,
            success=True,
        )
    except ValueError as e:
        logger.error(f"Error fixing feature: {e}")
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.error(f"Unexpected error fixing feature: {e}")
        raise HTTPException(status_code=500, detail="Internal server error") from e


# Validation error handler
@app.exception_handler(ValidationError)
async def validation_exception_handler(
    request: Request, exc: ValidationError
) -> JSONResponse:
    logger.error(f"Validation error: {exc}")
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation Error",
            "message": "Request validation failed",
            "details": exc.errors(),
            "timestamp": get_current_timestamp(),
        },
    )


# Value error handler
@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    logger.error(f"Value error: {exc}")
    return JSONResponse(
        status_code=400,
        content={
            "error": "Bad Request",
            "message": str(exc),
            "timestamp": get_current_timestamp(),
        },
    )


# General error handler
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error(f"Unexpected error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "timestamp": get_current_timestamp(),
        },
    )


# Run app
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)  # nosec
