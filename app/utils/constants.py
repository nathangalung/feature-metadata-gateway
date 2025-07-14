# Feature types
FEATURE_TYPES = ["batch", "real-time", "compute-first"]

# Data types
DATA_TYPES = [
    "string",
    "float",
    "integer",
    "boolean",
    "double",
    "bigint",
    "int",
    "decimal",
]

# User roles
USER_ROLES = ["developer", "tester", "approver"]

# Actions
ACTIONS = [
    "create",
    "update",
    "delete",
    "ready_for_testing",
    "fix",
    "approve",
    "test",
    "reject",
    "deploy",
]

# Role permissions
ROLE_PERMISSIONS = {
    "developer": {
        "create": True,
        "update": True,
        "delete": True,
        "ready_for_testing": True,
        "fix": True,
        "approve": False,
        "test": False,
        "reject": False,
        "deploy": False,
    },
    "tester": {
        "create": False,
        "update": False,
        "delete": False,
        "ready_for_testing": False,
        "fix": False,
        "approve": False,
        "test": True,
        "reject": False,
        "deploy": False,
    },
    "approver": {
        "create": False,
        "update": False,
        "delete": False,
        "ready_for_testing": False,
        "fix": False,
        "approve": True,
        "test": False,
        "reject": True,
        "deploy": True,
    },
}

# Status hierarchy
STATUS_HIERARCHY = {
    "DRAFT": 0,
    "READY_FOR_TESTING": 1,
    "TEST_SUCCEEDED": 2,
    "TEST_FAILED": 2,
    "APPROVED": 3,
    "REJECTED": 3,
    "DEPLOYED": 4,
    "DELETED": 5,
}

# Status transitions per role
STATUS_TRANSITIONS = {
    "developer": {
        "DRAFT": ["READY_FOR_TESTING"],
        "READY_FOR_TESTING": ["DRAFT"],
        "TEST_FAILED": ["DRAFT"],
        "REJECTED": ["DRAFT"],
    },
    "tester": {"READY_FOR_TESTING": ["TEST_SUCCEEDED", "TEST_FAILED"]},
    "approver": {"TEST_SUCCEEDED": ["APPROVED", "REJECTED"], "APPROVED": ["DEPLOYED"]},
}

# Critical fields
CRITICAL_FIELDS = ["query", "feature_type", "feature_data_type"]
