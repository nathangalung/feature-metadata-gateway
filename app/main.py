from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .models.request import FeatureRequest
from .models.response import EntityResult, FeatureResponse, FeatureValue
from .services.dummy_features import FEATURE_REGISTRY
from .services.feature_service import FeatureService
from .utils.timestamp import get_current_timestamp_ms

app = FastAPI(title="Feature Metadata Gateway", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"])
feature_service = FeatureService()


@app.get("/health")
async def health_check():
    """Health check"""
    return {"status": "ok", "timestamp": get_current_timestamp_ms()}


@app.post("/features", response_model=FeatureResponse)
async def get_features(request: FeatureRequest):
    """Get feature metadata with values"""
    try:
        current_timestamp = request.event_timestamp or get_current_timestamp_ms()

        # Process batch request
        response_data = await feature_service.batch_process_features(
            request.features, request.entities, current_timestamp
        )

        # Convert to response format
        results = []
        for result_data in response_data["results"]:
            # Convert feature values to FeatureValue objects
            converted_values = []
            for i, value in enumerate(result_data["values"]):
                if i == 0:  # First value is entity ID (string)
                    converted_values.append(value)
                elif isinstance(value, dict):
                    converted_values.append(FeatureValue(**value))
                else:
                    converted_values.append(value)

            results.append(
                EntityResult(
                    values=converted_values,
                    statuses=result_data["statuses"],
                    event_timestamps=result_data["event_timestamps"],
                )
            )

        return FeatureResponse(metadata=response_data["metadata"], results=results)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}") from e


@app.get("/features/available")
async def list_features():
    """List available features"""
    return {"available_features": list(FEATURE_REGISTRY.keys())}
