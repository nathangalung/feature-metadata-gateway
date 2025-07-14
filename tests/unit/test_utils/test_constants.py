from app.utils.constants import (
    ACTIONS,
    CRITICAL_FIELDS,
    DATA_TYPES,
    FEATURE_TYPES,
    ROLE_PERMISSIONS,
    STATUS_HIERARCHY,
    STATUS_TRANSITIONS,
    USER_ROLES,
)


class TestConstants:
    """Test constants definitions."""

    # Feature types
    def test_feature_types(self):
        assert FEATURE_TYPES == ["batch", "real-time", "compute-first"]

    # Data types
    def test_data_types(self):
        assert set(DATA_TYPES) == {
            "string",
            "float",
            "integer",
            "boolean",
            "double",
            "bigint",
            "int",
            "decimal",
        }

    # User roles
    def test_user_roles(self):
        assert set(USER_ROLES) == {"developer", "tester", "approver"}

    # Actions
    def test_actions(self):
        for action in [
            "create",
            "update",
            "delete",
            "ready_for_testing",
            "fix",
            "approve",
            "test",
            "reject",
            "deploy",
        ]:
            assert action in ACTIONS

    # Role permissions
    def test_role_permissions(self):
        assert ROLE_PERMISSIONS["developer"]["create"]
        assert not ROLE_PERMISSIONS["developer"]["approve"]
        assert ROLE_PERMISSIONS["tester"]["test"]
        assert not ROLE_PERMISSIONS["tester"]["approve"]
        assert ROLE_PERMISSIONS["approver"]["approve"]
        assert ROLE_PERMISSIONS["approver"]["deploy"]

    # Status hierarchy
    def test_status_hierarchy(self):
        assert STATUS_HIERARCHY["DRAFT"] == 0
        assert STATUS_HIERARCHY["READY_FOR_TESTING"] == 1
        assert STATUS_HIERARCHY["TEST_SUCCEEDED"] == 2
        assert STATUS_HIERARCHY["DEPLOYED"] == 4
        assert STATUS_HIERARCHY["DELETED"] == 5
        assert STATUS_HIERARCHY["REJECTED"] == 3

    # Status transitions
    def test_status_transitions(self):
        assert "DRAFT" in STATUS_TRANSITIONS["developer"]
        assert "READY_FOR_TESTING" in STATUS_TRANSITIONS["tester"]
        assert "TEST_SUCCEEDED" in STATUS_TRANSITIONS["approver"]

    # Critical fields
    def test_critical_fields(self):
        for field in ["query", "feature_type", "feature_data_type"]:
            assert field in CRITICAL_FIELDS
