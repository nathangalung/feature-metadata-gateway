import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.models.request import FeatureRequest
from app.models.response import EntityResult, FeatureResponse, FeatureValue
from app.services.feature_service import FeatureService
from app.utils.timestamp import get_current_timestamp_ms

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Feature Metadata Gateway", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize feature service
feature_service = FeatureService()


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "timestamp": get_current_timestamp_ms()}


@app.get("/features/available")
async def get_available_features():
    """Get available features list"""
    features = feature_service.get_available_features()
    return {"available_features": features}


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
                if i == 0:  # First value is entity ID
                    converted_values.append(value)
                elif isinstance(value, dict):
                    # Convert dict to FeatureValue
                    converted_values.append(FeatureValue(**value))
                else:
                    # Handle null values (for failed features)
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
        logger.exception("Error processing request")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}") from e
