"""Tests for validation utilities."""
from app.utils.validation import FeatureValidator, RoleValidator


class TestFeatureValidator:
    """Test FeatureValidator logic."""

    def test_validate_feature_name(self):
        assert FeatureValidator.validate_feature_name("cat:name:1")
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

    def test_validate_status_transition(self):
        assert FeatureValidator.validate_status_transition("DRAFT", "READY_FOR_TESTING", "developer")
        assert not FeatureValidator.validate_status_transition("DRAFT", "DEPLOYED", "developer")

    def test_is_critical_field_update(self):
        assert FeatureValidator.is_critical_field_update("query")
        assert not FeatureValidator.is_critical_field_update("description")

    def test_validate_sql_query(self):
        assert FeatureValidator.validate_sql_query("SELECT * FROM table")
        assert not FeatureValidator.validate_sql_query("DROP TABLE users")

    def test_sanitize_input(self):
        assert "<" not in FeatureValidator.sanitize_input("<script>")
        assert "&" not in FeatureValidator.sanitize_input("a&b")

    def test_validate_feature_metadata(self):
        valid = {
            "feature_name": "cat:name:1",
            "feature_type": "batch",
            "feature_data_type": "float",
            "query": "SELECT * FROM t",
            "description": "desc",
            "created_by": "dev"
        }
        assert FeatureValidator.validate_feature_metadata(valid) == {}

        invalid = {
            "feature_name": "badname",
            "feature_type": "badtype",
            "feature_data_type": "badtype",
            "query": "DROP",
            "description": "",
            "created_by": ""
        }
        errors = FeatureValidator.validate_feature_metadata(invalid)
        assert "feature_name" in errors
        assert "feature_type" in errors
        assert "feature_data_type" in errors
        assert "query" in errors
        assert "description" in errors
        assert "created_by" in errors

class TestRoleValidator:
    """Test RoleValidator logic."""

    def test_can_perform_action(self):
        allowed, _ = RoleValidator.can_perform_action("developer", "create")
        denied, msg = RoleValidator.can_perform_action("developer", "approve")
        assert allowed
        assert not denied
        assert "cannot perform action" in msg

    def test_validate_workflow_transition(self):
        allowed, _ = RoleValidator.validate_workflow_transition("developer", "DRAFT", "READY_FOR_TESTING")
        denied, msg = RoleValidator.validate_workflow_transition("developer", "DRAFT", "DEPLOYED")
        assert allowed
        assert not denied
        assert "Invalid status transition" in msg
