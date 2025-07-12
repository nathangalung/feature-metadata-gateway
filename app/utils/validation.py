import re
from typing import Any

from app.utils.constants import (CRITICAL_FIELDS, DATA_TYPES, FEATURE_TYPES,
                                 ROLE_PERMISSIONS, STATUS_TRANSITIONS,
                                 USER_ROLES)

MAX_FEATURE_NAME_LENGTH = 255


class FeatureValidator:
    """Feature validation utilities."""

    @staticmethod
    def validate_feature_name(feature_name: str) -> bool:
        """Validate feature name format.

        Accepts names like driver_hourly_stats:conv_rate:1, cat:name:1, and cat:name:v1.
        """
        if (
            not feature_name
            or not isinstance(feature_name, str)
            or len(feature_name) > MAX_FEATURE_NAME_LENGTH
        ):
            return False
        # Accept exactly 3 colon-separated non-empty parts, all alphanum/underscore, no spaces/dashes
        parts = feature_name.split(":")
        if len(parts) != 3 or not all(parts):
            return False
        category, name, version = parts
        # category and name: must start with letter/underscore, then alphanum/underscore
        if not re.fullmatch(r"[a-zA-Z_][a-zA-Z0-9_]*", category):
            return False
        if not re.fullmatch(r"[a-zA-Z_][a-zA-Z0-9_]*", name):
            return False
        # version: v+digits or digits only
        if not (
            re.fullmatch(r"v[1-9][0-9]*", version)
            or re.fullmatch(r"[1-9][0-9]*", version)
        ):
            return False
        return True

    @staticmethod
    def validate_feature_type(feature_type: str) -> bool:
        """Validate feature type."""
        return feature_type in FEATURE_TYPES

    @staticmethod
    def validate_data_type(data_type: str) -> bool:
        """Validate data type."""
        return data_type in DATA_TYPES

    @staticmethod
    def validate_user_role(user_role: str) -> bool:
        """Validate user role."""
        return user_role in USER_ROLES

    @staticmethod
    def validate_role_permission(user_role: str, action: str) -> bool:
        """Validate role permission."""
        if user_role not in ROLE_PERMISSIONS:
            return False
        permissions = ROLE_PERMISSIONS.get(user_role, {})
        return permissions.get(action, False)

    @staticmethod
    def validate_role_action(user_role: str, action: str) -> None:
        """Validate role action."""
        if not FeatureValidator.validate_user_role(user_role):
            raise ValueError(f"User role {user_role} cannot perform action {action}")
        if not FeatureValidator.validate_role_permission(user_role, action):
            raise ValueError(f"User role {user_role} cannot perform action {action}")

    @staticmethod
    def validate_status_transition(
        current_status: str, new_status: str, user_role: str
    ) -> bool:
        """Validate status transition."""
        if user_role not in STATUS_TRANSITIONS:
            return False
        role_transitions = STATUS_TRANSITIONS[user_role]
        allowed_transitions = role_transitions.get(current_status, [])
        return new_status in allowed_transitions

    @staticmethod
    def is_critical_field_update(field_name: str) -> bool:
        """Check if field is critical."""
        return field_name in CRITICAL_FIELDS

    @staticmethod
    def validate_sql_query(query: str) -> bool:
        """Validate SQL query.

        Accepts any non-empty, non-whitespace string except dangerous queries like DROP/DELETE.
        """
        if not query or not isinstance(query, str) or not query.strip():
            return False
        lowered = query.strip().lower()
        # Disallow dangerous queries
        if lowered.startswith("drop") or lowered.startswith("delete"):
            return False
        return True

    @staticmethod
    def sanitize_input(input_str: str) -> str:
        """Sanitize input."""
        if not isinstance(input_str, str):
            return str(input_str)
        dangerous_chars = ["<", ">", '"', "'", "&", "\x00"]
        sanitized = input_str
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, "")
        return sanitized.strip()

    @staticmethod
    def validate_feature_metadata(metadata: dict[str, Any]) -> dict[str, str]:
        """Validate feature metadata."""
        errors = {}
        required_fields = [
            "feature_name",
            "feature_type",
            "feature_data_type",
            "query",
            "description",
            "created_by",
        ]
        for field in required_fields:
            if (
                field not in metadata
                or metadata[field] is None
                or (isinstance(metadata[field], str) and not metadata[field].strip())
            ):
                errors[field] = f"{field} is required"
        if "feature_name" in metadata and metadata.get("feature_name"):
            if not FeatureValidator.validate_feature_name(metadata["feature_name"]):
                errors["feature_name"] = "Invalid feature name format"
        if "feature_type" in metadata and metadata.get("feature_type"):
            if not FeatureValidator.validate_feature_type(metadata["feature_type"]):
                errors["feature_type"] = (
                    f"Invalid feature type. Must be one of: {FEATURE_TYPES}"
                )
        if "feature_data_type" in metadata and metadata.get("feature_data_type"):
            if not FeatureValidator.validate_data_type(metadata["feature_data_type"]):
                errors["feature_data_type"] = (
                    f"Invalid data type. Must be one of: {DATA_TYPES}"
                )
        if "query" in metadata and metadata.get("query"):
            if not FeatureValidator.validate_sql_query(metadata["query"]):
                errors["query"] = "Invalid SQL query format"
        return errors


class RoleValidator:
    """Role-based validation utilities."""

    ROLE_ACTIONS = {
        "developer": {"create", "update", "delete", "ready_for_testing", "fix"},
        "external_testing_system": {"test"},
        "approver": {"approve", "reject"},
    }

    @staticmethod
    def can_perform_action(user_role: str, action: str):
        if user_role not in RoleValidator.ROLE_ACTIONS:
            # For test compatibility, always return "User role ... cannot perform action ..."
            return False, f"User role {user_role} cannot perform action {action}"
        if action not in RoleValidator.ROLE_ACTIONS[user_role]:
            return False, f"User role {user_role} cannot perform action {action}"
        return True, ""

    @staticmethod
    def validate_workflow_transition(
        user_role: str, current_status: str, target_status: str
    ) -> tuple[bool, str]:
        """Validate workflow transition."""
        if not FeatureValidator.validate_status_transition(
            current_status, target_status, user_role
        ):
            return (
                False,
                f"Invalid status transition from {current_status} to {target_status} for role {user_role}",
            )
        return True, "Transition allowed"
