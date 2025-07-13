"""Tests for validation utilities."""

import pytest

from app.utils.validation import FeatureValidator, RoleValidator


class TestFeatureValidator:
    """Test FeatureValidator logic."""

    def test_validate_feature_name(self):
        assert FeatureValidator.validate_feature_name("cat:name:1")
        assert FeatureValidator.validate_feature_name("cat:name:v1")
        assert not FeatureValidator.validate_feature_name("invalidname")

    def test_validate_feature_type(self):
        assert FeatureValidator.validate_feature_type("batch")
        assert not FeatureValidator.validate_feature_type("invalid")

    def test_validate_data_type(self):
        assert FeatureValidator.validate_data_type("float")
        assert not FeatureValidator.validate_data_type("notatype")

    def test_validate_user_role(self):
        assert FeatureValidator.validate_user_role("developer")
        assert not FeatureValidator.validate_user_role("admin")

    def test_validate_role_permission(self):
        assert FeatureValidator.validate_role_permission("developer", "create")
        assert not FeatureValidator.validate_role_permission("developer", "approve")
        # Line 80: user_role not in ROLE_PERMISSIONS
        assert not FeatureValidator.validate_role_permission("notarole", "create")

    def test_validate_role_action(self):
        # Line 72: user_role not valid
        with pytest.raises(ValueError):
            FeatureValidator.validate_role_action("notarole", "create")
        # Line 72: valid role, but not allowed action
        with pytest.raises(ValueError):
            FeatureValidator.validate_role_action("developer", "approve")

    def test_validate_status_transition(self):
        assert FeatureValidator.validate_status_transition(
            "DRAFT", "READY_FOR_TESTING", "developer"
        )
        assert not FeatureValidator.validate_status_transition(
            "DRAFT", "DEPLOYED", "developer"
        )

    def test_is_critical_field_update(self):
        assert FeatureValidator.is_critical_field_update("query")
        assert not FeatureValidator.is_critical_field_update("description")

    def test_validate_sql_query(self):
        assert FeatureValidator.validate_sql_query("SELECT * FROM table")
        assert not FeatureValidator.validate_sql_query("DROP TABLE users")
        assert not FeatureValidator.validate_sql_query("")
        assert not FeatureValidator.validate_sql_query("   ")
        assert not FeatureValidator.validate_sql_query(None)

    def test_sanitize_input(self):
        assert "<" not in FeatureValidator.sanitize_input("<script>")
        assert "&" not in FeatureValidator.sanitize_input("a&b")
        assert FeatureValidator.sanitize_input(123) == "123"

    def test_validate_feature_metadata(self):
        valid = {
            "feature_name": "cat:name:1",
            "feature_type": "batch",
            "feature_data_type": "float",
            "query": "SELECT * FROM t",
            "description": "desc",
            "created_by": "dev",
        }
        assert FeatureValidator.validate_feature_metadata(valid) == {}

        invalid = {
            "feature_name": "badname",
            "feature_type": "badtype",
            "feature_data_type": "badtype",
            "query": "DROP",
            "description": "",
            "created_by": "",
        }
        errors = FeatureValidator.validate_feature_metadata(invalid)
        assert "feature_name" in errors
        assert "feature_type" in errors
        assert "feature_data_type" in errors
        assert "query" in errors
        assert "description" in errors
        assert "created_by" in errors

    def test_validate_feature_name_edge_cases(self):
        # Too long
        long_name = "a" * 256 + ":b:1"
        assert not FeatureValidator.validate_feature_name(long_name)
        # Not a string
        assert not FeatureValidator.validate_feature_name(123)
        # Not exactly 3 parts
        assert not FeatureValidator.validate_feature_name("a:b")
        assert not FeatureValidator.validate_feature_name("a:b:c:d")
        # Empty parts
        assert not FeatureValidator.validate_feature_name("a:b:")
        assert not FeatureValidator.validate_feature_name(":b:c")
        # Invalid category/name regex
        assert not FeatureValidator.validate_feature_name("1abc:name:1")
        assert not FeatureValidator.validate_feature_name("abc:1name:1")
        # Invalid version
        assert not FeatureValidator.validate_feature_name("abc:name:v0")
        assert not FeatureValidator.validate_feature_name("abc:name:0")
        assert not FeatureValidator.validate_feature_name("abc:name:v")
        assert not FeatureValidator.validate_feature_name("abc:name:v01")

    def test_validate_feature_name_none_and_empty(self):
        assert not FeatureValidator.validate_feature_name(None)
        assert not FeatureValidator.validate_feature_name("")
        # Also test whitespace string
        assert not FeatureValidator.validate_feature_name("   ")

    def test_validate_status_transition_invalid_role(self):
        # This covers the branch where user_role is not in STATUS_TRANSITIONS
        assert not FeatureValidator.validate_status_transition(
            "DRAFT", "READY_FOR_TESTING", "notarole"
        )

    def test_validate_sql_query_non_str(self):
        # Covers the branch where query is not a string
        assert not FeatureValidator.validate_sql_query(123)
        assert not FeatureValidator.validate_sql_query([])

    def test_sanitize_input_edge_cases(self):
        # Covers sanitize_input with non-str and str with all dangerous chars
        assert FeatureValidator.sanitize_input(None) == "None"
        assert FeatureValidator.sanitize_input("<>'\"&\x00") == ""


class TestRoleValidator:
    """Test RoleValidator logic."""

    def test_can_perform_action(self):
        allowed, _ = RoleValidator.can_perform_action("developer", "create")
        denied, msg = RoleValidator.can_perform_action("developer", "approve")
        assert allowed
        assert not denied
        assert "cannot perform action" in msg

    def test_validate_workflow_transition(self):
        allowed, _ = RoleValidator.validate_workflow_transition(
            "developer", "DRAFT", "READY_FOR_TESTING"
        )
        denied, msg = RoleValidator.validate_workflow_transition(
            "developer", "DRAFT", "DEPLOYED"
        )
        assert allowed
        assert not denied
        assert "Invalid status transition" in msg
