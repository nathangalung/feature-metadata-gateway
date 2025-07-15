import logging
import threading
from contextlib import asynccontextmanager
from typing import Any

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.models.request import (
    ApproveFeatureMetadataRequest,
    CreateFeatureMetadataRequest,
    DeleteFeatureMetadataRequest,
    GetFeatureMetadataRequest,
    RejectFeatureMetadataRequest,
    SubmitTestFeatureMetadataRequest,
    TestFeatureMetadataRequest,
    UpdateFeatureMetadataRequest,
)
from app.models.response import (
    CreateFeatureMetadataResponse,
    DeleteFeatureMetadataResponse,
    FeatureMetadataBatchResponse,
    FeatureMetadataSingleResponse,
    HealthResponse,
    UpdateFeatureMetadataResponse,
    WorkflowMetadataResponse,
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
_service_lock = threading.Lock()


# Ensure service initialized
def ensure_service() -> None:
    global feature_service
    with _service_lock:
        if feature_service is None:
            feature_service = FeatureMetadataService()


# App lifespan context
@asynccontextmanager
async def lifespan(app: FastAPI) -> Any:
    global feature_service
    with _service_lock:
        feature_service = FeatureMetadataService()
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


# Root endpoint
@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Feature Metadata Gateway"}


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


# Create feature metadata
@app.post(
    "/create_feature_metadata",
    response_model=CreateFeatureMetadataResponse,
    status_code=201,
)
async def create_feature_metadata(
    request: CreateFeatureMetadataRequest,
) -> CreateFeatureMetadataResponse:
    try:
        ensure_service()
        with _service_lock:
            if feature_service is None:
                raise HTTPException(status_code=500, detail="Service not initialized")
            metadata = feature_service.create_feature_metadata(request.model_dump())
        return CreateFeatureMetadataResponse(
            message="Feature metadata created successfully",
            metadata=metadata,
            request_id=None,
            success=True,
        )
    except ValueError as e:
        logger.error(f"Error creating metadata: {e}")
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.error(f"Unexpected error creating metadata: {e}")
        raise HTTPException(status_code=500, detail="Internal server error") from e


# Get feature metadata (POST single/multiple)
@app.post(
    "/get_feature_metadata",
    response_model=FeatureMetadataSingleResponse | FeatureMetadataBatchResponse,
)
async def get_feature_metadata(
    request: GetFeatureMetadataRequest,
) -> FeatureMetadataSingleResponse | FeatureMetadataBatchResponse:
    try:
        ensure_service()
        if feature_service is None:
            raise HTTPException(status_code=500, detail="Service not initialized")
        features = request.features
        user_role = request.user_role
        if isinstance(features, str):
            metadata = feature_service.get_feature_metadata(features, user_role)
            return FeatureMetadataSingleResponse(
                values=metadata.dict(),
                status="200 OK",
                event_timestamp=get_current_timestamp(),
            )
        elif isinstance(features, list):
            values = []
            status_list = []
            ts_list = []
            found_features = []
            for fname in features:
                try:
                    meta = feature_service.get_feature_metadata(fname, user_role)
                    values.append(meta.dict())
                    status_list.append("200 OK")
                    ts_list.append(get_current_timestamp())
                    found_features.append(fname)
                except Exception as e:
                    values.append({})
                    status_list.append(str(e))
                    ts_list.append(get_current_timestamp())
                    found_features.append(fname)
            return FeatureMetadataBatchResponse(
                metadata={"features": found_features},
                results={
                    "values": values,
                    "status/message": status_list,
                    "event_timestamp": ts_list,
                },
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid features type")
    except ValueError as e:
        logger.error(f"Error getting metadata: {e}")
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        logger.error(f"Unexpected error getting metadata: {e}")
        raise HTTPException(status_code=500, detail="Internal server error") from e


# Get all feature metadata (POST with filters)
@app.post("/get_all_feature_metadata")
async def get_all_feature_metadata(request: dict) -> dict[str, Any]:
    try:
        ensure_service()
        if feature_service is None:
            raise HTTPException(status_code=500, detail="Service not initialized")
        user_role = str(request.get("user_role") or "")
        from app.utils.validation import FeatureValidator

        if not FeatureValidator.validate_user_role(user_role):
            raise HTTPException(status_code=400, detail="Invalid role")
        filters = {
            k: v for k, v in request.items() if k != "user_role" and v is not None
        }
        result = feature_service.get_all_feature_metadata(user_role, filters)
        return {
            "metadata": [meta.dict() for meta in result.values()],
            "total_count": len(result),
        }
    except HTTPException as e:
        raise e
    except ValueError as e:
        logger.error(f"Error getting all metadata: {e}")
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.error(f"Unexpected error getting all metadata: {e}")
        raise HTTPException(status_code=500, detail="Internal server error") from e


# Update feature metadata
@app.post("/update_feature_metadata", response_model=UpdateFeatureMetadataResponse)
async def update_feature_metadata(
    request: UpdateFeatureMetadataRequest,
) -> UpdateFeatureMetadataResponse:
    try:
        ensure_service()
        with _service_lock:
            if feature_service is None:
                raise HTTPException(status_code=500, detail="Service not initialized")
            metadata = feature_service.update_feature_metadata(request.model_dump())
        return UpdateFeatureMetadataResponse(
            message="Feature metadata updated successfully",
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


# Delete feature metadata
@app.post("/delete_feature_metadata", response_model=DeleteFeatureMetadataResponse)
async def delete_feature_metadata(
    request: DeleteFeatureMetadataRequest,
) -> DeleteFeatureMetadataResponse:
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
        return DeleteFeatureMetadataResponse(
            message="Feature metadata deleted successfully",
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


# Submit for testing
@app.post("/submit_test_feature_metadata", response_model=WorkflowMetadataResponse)
async def submit_test_feature_metadata(
    request: SubmitTestFeatureMetadataRequest,
) -> WorkflowMetadataResponse:
    try:
        ensure_service()
        with _service_lock:
            if feature_service is None:
                raise HTTPException(status_code=500, detail="Service not initialized")
            metadata = feature_service.submit_test_feature_metadata(
                request.model_dump()
            )
        return WorkflowMetadataResponse(
            message="Feature submitted for testing",
            metadata=metadata,
            previous_status="DRAFT",
            new_status="READY_FOR_TESTING",
            request_id=None,
            success=True,
        )
    except ValueError as e:
        logger.error(f"Error submitting feature for testing: {e}")
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.error(f"Unexpected error submitting feature for testing: {e}")
        raise HTTPException(status_code=500, detail="Internal server error") from e


# Test feature metadata
@app.post("/test_feature_metadata", response_model=WorkflowMetadataResponse)
async def test_feature_metadata(
    request: TestFeatureMetadataRequest,
) -> WorkflowMetadataResponse:
    try:
        ensure_service()
        with _service_lock:
            if feature_service is None:
                raise HTTPException(status_code=500, detail="Service not initialized")
            metadata = feature_service.test_feature_metadata(request.model_dump())
        return WorkflowMetadataResponse(
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


# Approve feature metadata
@app.post("/approve_feature_metadata", response_model=WorkflowMetadataResponse)
async def approve_feature_metadata(
    request: ApproveFeatureMetadataRequest,
) -> WorkflowMetadataResponse:
    try:
        ensure_service()
        with _service_lock:
            if feature_service is None:
                raise HTTPException(status_code=500, detail="Service not initialized")
            metadata = feature_service.approve_feature_metadata(request.model_dump())
        return WorkflowMetadataResponse(
            message="Feature approved and deployed",
            metadata=metadata,
            previous_status="TEST_SUCCEEDED",
            new_status="DEPLOYED",
            request_id=None,
            success=True,
        )
    except ValueError as e:
        logger.error(f"Error approving feature: {e}")
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.error(f"Unexpected error approving feature: {e}")
        raise HTTPException(status_code=500, detail="Internal server error") from e


# Reject feature metadata
@app.post("/reject_feature_metadata", response_model=WorkflowMetadataResponse)
async def reject_feature_metadata(
    request: RejectFeatureMetadataRequest,
) -> WorkflowMetadataResponse:
    try:
        ensure_service()
        with _service_lock:
            if feature_service is None:
                raise HTTPException(status_code=500, detail="Service not initialized")
            metadata = feature_service.reject_feature_metadata(request.model_dump())
        return WorkflowMetadataResponse(
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
    uvicorn.run(app, host="0.0.0.0", port=8000)
