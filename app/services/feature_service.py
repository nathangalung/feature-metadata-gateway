import asyncio
import json
import logging
import random
from pathlib import Path
from typing import Any

from ..utils.timestamp import get_current_timestamp_ms
from .dummy_features import FEATURE_REGISTRY

logger = logging.getLogger(__name__)

# Constants
FEATURE_FORMAT_PARTS = 3
STATUS_HIERARCHY = {"READY FOR TESTING": 0, "TESTED": 1, "APPROVED": 2, "DEPLOYED": 3}


class FeatureService:
    """Feature metadata service"""

    def __init__(self):
        """Initialize with features"""
        self.feature_metadata = self._load_metadata()

    def _load_metadata(self) -> dict[str, dict[str, Any]]:
        """Load metadata from JSON"""
        try:
            data_path = Path(__file__).parent.parent.parent / "data" / "feature_metadata.json"
            if data_path.exists():
                content = data_path.read_text()
                # Parse only the first JSON object
                lines = content.strip().split("\n")
                first_json_end = 0
                brace_count = 0
                for i, line in enumerate(lines):
                    brace_count += line.count("{") - line.count("}")
                    if brace_count == 0 and i > 0:
                        first_json_end = i
                        break

                first_json = "\n".join(lines[: first_json_end + 1])
                return json.loads(first_json)
            return self._default_metadata()
        except (json.JSONDecodeError, OSError):
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
                "description": "Average daily trips for driver",
                "status": "READY FOR TESTING",
            },
        }

    def _validate_feature_format(self, feature_name: str) -> bool:
        """Validate feature format: category:name:version"""
        parts = feature_name.split(":")
        return len(parts) == FEATURE_FORMAT_PARTS and all(part.strip() for part in parts)

    def _can_edit_feature(self, status: str) -> bool:
        """Check if feature can be edited"""
        return status != "DEPLOYED"

    def _generate_feature_value(self, feature_name: str, entity_id: str) -> float | int | str:
        """Generate deterministic feature value"""
        # Create unique hash combining feature and entity
        combined = f"{feature_name}#{entity_id}"
        hash_val = abs(hash(combined))

        # Use different seeds for different combinations
        seed = (hash_val + len(feature_name) + len(entity_id)) % (2**31)
        random.seed(seed)

        # Get feature metadata
        feature = FEATURE_REGISTRY.get(feature_name)
        if feature:
            metadata = feature.generate_metadata(get_current_timestamp_ms())
            data_type = metadata.get("feature_data_type", "float")
        else:
            data_type = "float"

        # Generate value based on type with more variation
        if data_type == "float":
            base_val = random.uniform(0.1, 0.9)
            # Add variation based on entity
            entity_factor = (hash(entity_id) % 100) / 1000.0
            return round(base_val + entity_factor, 2)
        if data_type == "integer":
            choices = [5, 7, 10000, 85, 250, 15, 42, 99, 150, 500]
            entity_index = hash(entity_id) % len(choices)
            feature_index = hash(feature_name) % len(choices)
            return choices[(entity_index + feature_index) % len(choices)]
        # string
        choices = ["hello", "world", "feature", "value", "test", "data", "sample", "output"]
        entity_index = hash(entity_id) % len(choices)
        feature_index = hash(feature_name) % len(choices)
        return choices[(entity_index + feature_index) % len(choices)]

    async def get_feature_metadata(
        self, feature_name: str, event_timestamp: int
    ) -> dict[str, Any] | None:
        """Get feature metadata"""
        await asyncio.sleep(0.005)

        # Validate format
        if not self._validate_feature_format(feature_name):
            return None

        feature = FEATURE_REGISTRY.get(feature_name)
        if not feature:
            return None

        try:
            return feature.generate_metadata(event_timestamp)
        except Exception:
            logger.exception("Feature metadata generation failed")
            return None

    async def get_feature_value_with_metadata(
        self, feature_name: str, entity_id: str, event_timestamp: int
    ) -> dict[str, Any] | None:
        """Get feature value with metadata"""
        metadata = await self.get_feature_metadata(feature_name, event_timestamp)
        if not metadata:
            return None

        value = self._generate_feature_value(feature_name, entity_id)

        return {
            "value": value,
            "feature_type": metadata.get("feature_type", "real-time"),
            "feature_data_type": metadata.get("feature_data_type", "float"),
            "query": metadata.get("query_sql", "sql_query"),
            "created_time": metadata.get("created_time", event_timestamp),
            "updated_time": metadata.get("updated_time", event_timestamp),
            "created_by": metadata.get("created_by", "system"),
            "last_updated_by": metadata.get("last_updated_by", "system"),
            "approved_by": metadata.get("approved_by"),
            "status": metadata.get("status"),
            "description": metadata.get("description"),
            "event_timestamp": event_timestamp,
        }

    async def batch_process_features(
        self, features: list[str], entities: dict[str, list[str]], event_timestamp: int
    ) -> dict[str, Any]:
        """Process batch feature request"""
        # Build feature names list
        entity_keys = list(entities.keys())
        feature_names = entity_keys + features

        results = []

        # Process each entity
        for entity_key in entity_keys:
            entity_ids = entities[entity_key]

            for entity_id in entity_ids:
                values = [entity_id]
                statuses = ["200 OK"]
                timestamps = [event_timestamp]

                # Process each feature
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
                            statuses.append("404 Not Found")
                            timestamps.append(event_timestamp)
                    except Exception:
                        logger.exception("Error processing feature %s", feature_name)
                        statuses.append("500 Internal Server Error")
                        timestamps.append(event_timestamp)

                results.append(
                    {"values": values, "statuses": statuses, "event_timestamps": timestamps}
                )

        return {"metadata": {"feature_names": feature_names}, "results": results}
