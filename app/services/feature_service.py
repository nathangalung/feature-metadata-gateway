import hashlib
import json
import logging
import random
from pathlib import Path
from typing import Any

from app.services.dummy_features import FEATURE_REGISTRY

logger = logging.getLogger(__name__)

# Constants
FEATURE_NAME_PARTS = 3
STATUS_HIERARCHY = {
    "READY FOR TESTING": 0,
    "TESTED": 1,
    "APPROVED": 2,
    "DEPLOYED": 3,
}


class FeatureService:
    """Feature metadata service"""

    def __init__(self):
        """Initialize with metadata loading"""
        self.feature_metadata = self._load_feature_metadata()

    def _load_feature_metadata(self) -> dict[str, dict[str, Any]]:
        """Load feature metadata from file"""
        metadata_file = Path("data/feature_metadata.json")

        if not metadata_file.exists():
            logger.warning("Metadata file not found, using defaults")
            return self._default_metadata()

        try:
            content = metadata_file.read_text()
            # Handle multiline JSON files
            lines = content.strip().split("\n")
            for line in lines:
                if line.strip():
                    try:
                        return json.loads(line)
                    except json.JSONDecodeError:
                        continue

            logger.warning("No valid JSON found, using defaults")
            return self._default_metadata()

        except (OSError, json.JSONDecodeError) as e:
            logger.exception("Failed to load metadata: %s", e)
            return self._default_metadata()

    def _default_metadata(self) -> dict[str, dict[str, Any]]:
        """Default feature metadata"""
        return {
            "driver_hourly_stats:conv_rate:1": {
                "feature_type": "real-time",
                "query_sql": "SELECT conv_rate FROM driver_hourly_stats WHERE driver_id = ?",
                "feature_data_type": "float",
                "description": "Conversion rate for driver",
                "status": "DEPLOYED",
            },
            "driver_hourly_stats:acc_rate:2": {
                "feature_type": "batch",
                "query_sql": "SELECT acc_rate FROM driver_hourly_stats WHERE driver_id = ?",
                "feature_data_type": "integer",
                "description": "Acceptance rate for driver",
                "status": "APPROVED",
            },
            "driver_hourly_stats:avg_daily_trips:3": {
                "feature_type": "real-time",
                "query_sql": "SELECT avg_daily_trips FROM driver_hourly_stats WHERE driver_id = ?",
                "feature_data_type": "string",
                "description": "Average daily trips",
                "status": "READY FOR TESTING",
            },
            "fraud:amount:v1": {
                "feature_type": "batch",
                "query_sql": "SELECT fraud_amount FROM fraud_detection WHERE transaction_id = ?",
                "feature_data_type": "float",
                "description": "Fraud amount detection",
                "status": "DEPLOYED",
            },
            "customer:income:v1": {
                "feature_type": "batch",
                "query_sql": "SELECT income FROM customer_profile WHERE cust_id = ?",
                "feature_data_type": "integer",
                "description": "Customer income data",
                "status": "APPROVED",
            },
        }

    def _validate_feature_format(self, feature_name: str) -> bool:
        """Validate feature name format"""
        if not feature_name or not isinstance(feature_name, str):
            return False

        parts = feature_name.split(":")
        if len(parts) != FEATURE_NAME_PARTS:
            return False

        # Check no empty parts
        return all(part.strip() for part in parts)

    def _can_edit_feature(self, status: str | None) -> bool:
        """Check if feature is editable"""
        if status is None:
            return True
        return status != "DEPLOYED"

    def _generate_feature_value(self, feature_name: str, entity_id: str) -> Any:
        """Generate deterministic feature value"""
        # Create deterministic seed from feature + entity
        seed_string = f"{feature_name}:{entity_id}"
        seed = int(hashlib.md5(seed_string.encode()).hexdigest()[:8], 16)
        random.seed(seed)

        # Determine data type from feature name
        if "conv_rate" in feature_name or "fraud:amount" in feature_name:
            return round(random.uniform(0.1, 0.9), 2)
        if "acc_rate" in feature_name or "customer:income" in feature_name:
            return random.choice([5, 7, 10000, 85, 250, 15, 42, 99, 150, 500])
        # String features
        return random.choice(
            ["hello", "world", "feature", "value", "test", "data", "sample", "output"]
        )

    def _create_error_placeholder(self, event_timestamp: int) -> dict[str, Any]:
        """Create placeholder for failed features"""
        return {
            "value": None,
            "feature_type": "unknown",
            "feature_data_type": "unknown",
            "query": "Feature not found",
            "created_time": event_timestamp,
            "updated_time": event_timestamp,
            "created_by": "system",
            "last_updated_by": "system",
            "approved_by": None,
            "status": "NOT_FOUND",
            "description": "Feature not available",
            "event_timestamp": event_timestamp,
        }

    async def get_feature_metadata(
        self, feature_name: str, event_timestamp: int
    ) -> dict[str, Any] | None:
        """Get feature metadata only"""
        try:
            if feature_name in FEATURE_REGISTRY:
                feature_class = FEATURE_REGISTRY[feature_name]
                return feature_class.generate_metadata(event_timestamp)
        except Exception:
            logger.exception("Error generating metadata for %s", feature_name)

        return None

    async def get_feature_value_with_metadata(
        self, feature_name: str, entity_id: str, event_timestamp: int
    ) -> dict[str, Any] | None:
        """Get feature value with metadata"""
        try:
            if feature_name in FEATURE_REGISTRY:
                feature_class = FEATURE_REGISTRY[feature_name]
                metadata = feature_class.generate_metadata(event_timestamp)

                # Generate deterministic value
                value = self._generate_feature_value(feature_name, entity_id)

                return {"value": value, **metadata}
        except Exception:
            logger.exception("Error processing feature %s", feature_name)

        return None

    async def batch_process_features(
        self, features: list[str], entities: dict[str, list[str]], event_timestamp: int
    ) -> dict[str, Any]:
        """Process batch feature request"""
        # Build feature names list (entity keys + features)
        entity_keys = list(entities.keys())
        feature_names = entity_keys + features

        results = []

        # Process each entity type and their IDs
        for entity_key in entity_keys:
            entity_ids = entities[entity_key]

            # Process each individual entity ID
            for entity_id in entity_ids:
                values = [entity_id]  # Start with entity ID
                statuses = ["200 OK"]  # Entity status
                timestamps = [event_timestamp]  # Entity timestamp

                # Process each feature for this entity
                for feature_name in features:
                    try:
                        feature_data = await self.get_feature_value_with_metadata(
                            feature_name, entity_id, event_timestamp
                        )
                        if feature_data:
                            values.append(feature_data)
                            statuses.append("200 OK")
                            timestamps.append(event_timestamp)
                        else:
                            # Feature not found - add error placeholder
                            error_placeholder = self._create_error_placeholder(event_timestamp)
                            values.append(error_placeholder)
                            statuses.append("404 Not Found")
                            timestamps.append(event_timestamp)
                    except Exception:
                        logger.exception("Error processing feature %s", feature_name)
                        error_placeholder = self._create_error_placeholder(event_timestamp)
                        values.append(error_placeholder)
                        statuses.append("500 Internal Server Error")
                        timestamps.append(event_timestamp)

                # Add result for this entity
                results.append(
                    {"values": values, "statuses": statuses, "event_timestamps": timestamps}
                )

        return {"metadata": {"feature_names": feature_names}, "results": results}

    def get_available_features(self) -> list[str]:
        """Get list of available features"""
        return list(FEATURE_REGISTRY.keys())
