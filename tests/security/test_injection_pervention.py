import pytest
from fastapi.testclient import TestClient

from app.main import app


class TestInjectionPrevention:
    @pytest.fixture(autouse=True)
    def setup(self):
        with TestClient(app) as client:
            self.client = client
            yield

    def test_sql_injection_prevention(self):
        sql_payloads = [
            "'; DROP TABLE features; --",
            "' OR '1'='1",
            "UNION SELECT * FROM users",
            "'; INSERT INTO users VALUES ('hacker'); --",
            "); DROP TABLE features; --",
        ]
        for i, payload in enumerate(sql_payloads):
            resp = self.client.post(
                "/create_feature_metadata",
                json={
                    "feature_name": f"security:sql:v{i}",
                    "feature_type": "batch",
                    "feature_data_type": "float",
                    "query": payload,
                    "description": "SQL injection test",
                    "created_by": "test_user",
                    "user_role": "developer",
                },
            )
            assert resp.status_code in [201, 400, 422]

    def test_nosql_injection_prevention(self):
        nosql_payloads = [
            {
                "features": ["test:feature:v1"],
                "entities": {"user_id": ["user_1", "user_2', $where: null, name: '"]},
            },
            {
                "features": ["test:feature:v1"],
                "entities": {"user_id": ["user_1", "{$gt: ''}"]},
            },
            {
                "features": ["test:feature:v1"],
                "entities": {"user_id": ["user_1", "'], $or: [{}, {}, {}], field: ["]},
            },
            {
                "features": ["test:feature:v1"],
                "entities": {
                    "user_id": ["user_1", "{$where: function() { return true }}"]
                },
            },
            {
                "features": ["test:feature:v1"],
                "entities": {"user_id": ["user_1", '{"$gt": ""}']},
            },
        ]
        for payload in nosql_payloads:
            resp = self.client.post("/get_feature_metadata", json=payload)
            assert resp.status_code in [400, 404, 422]

    def test_command_injection_prevention(self):
        cmd_payloads = [
            "`ls -la`",
            "$(cat /etc/passwd)",
            "& echo vulnerable",
            "; rm -rf /",
            "| cat /etc/shadow",
        ]
        for i, payload in enumerate(cmd_payloads):
            resp = self.client.post(
                "/create_feature_metadata",
                json={
                    "feature_name": f"security:cmd:v{i}",
                    "feature_type": "batch",
                    "feature_data_type": "float",
                    "query": "SELECT value FROM table",
                    "description": payload,
                    "created_by": "test_user",
                    "user_role": "developer",
                },
            )
            assert resp.status_code in [201, 400, 422]

    def test_xss_prevention(self):
        xss_payloads = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "<a href=\"javascript:alert('xss')\">click me</a>",
            "<div onmouseover=\"alert('xss')\">hover</div>",
        ]
        for i, payload in enumerate(xss_payloads):
            resp = self.client.post(
                "/create_feature_metadata",
                json={
                    "feature_name": f"security:xss:v{i}",
                    "feature_type": "batch",
                    "feature_data_type": "float",
                    "query": "SELECT value FROM table",
                    "description": payload,
                    "created_by": "test_user",
                    "user_role": "developer",
                },
            )
            assert resp.status_code in [201, 400, 422]
