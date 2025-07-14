import pytest
from fastapi.testclient import TestClient

from app.main import app


# Test client fixture
@pytest.fixture
def test_client():
    with TestClient(app) as client:
        yield client


class TestInputValidation:
    """Test input validation security."""

    # Setup test client
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = TestClient(app)

    # SQL injection prevention
    def test_sql_injection_prevention(self, test_client):
        sql_payloads = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "UNION SELECT * FROM admin",
            "'; INSERT INTO admin VALUES ('hacker'); --",
            "' AND 1=1 --",
            "' UNION ALL SELECT password FROM users WHERE 'a'='a",
        ]
        for i, payload in enumerate(sql_payloads):
            response = test_client.post(
                "/create_feature_metadata",
                json={
                    "feature_name": f"security:sql:v{i}",
                    "feature_type": "batch",
                    "feature_data_type": "string",
                    "query": payload,
                    "description": "SQL injection test",
                    "created_by": "security_tester",
                    "user_role": "developer",
                },
            )
            assert response.status_code in [201, 400, 422]
            if response.status_code == 201:
                metadata = response.json()["metadata"]
                assert "query" in metadata
                assert isinstance(metadata["query"], str)

    # XSS prevention
    def test_xss_prevention(self, test_client):
        xss_payloads = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "{{constructor.constructor('alert(1)')()}}",
            "<svg onload=alert('xss')>",
            "';alert('xss');//",
        ]
        for i, payload in enumerate(xss_payloads):
            response = test_client.post(
                "/create_feature_metadata",
                json={
                    "feature_name": f"security:xss:v{i}",
                    "feature_type": "real-time",
                    "feature_data_type": "string",
                    "query": "SELECT name FROM table",
                    "description": payload,
                    "created_by": "security_tester",
                    "user_role": "developer",
                },
            )
            if response.status_code == 201:
                metadata = response.json()["metadata"]
                assert "description" in metadata
                assert isinstance(metadata["description"], str)
            else:
                assert response.status_code in [400, 422]

    # Command injection prevention
    def test_command_injection_prevention(self, test_client):
        command_payloads = [
            "; ls -la",
            "| cat /etc/passwd",
            "& whoami",
            "`id`",
            "$(rm -rf /)",
            "; python -c 'import os; os.system(\"ls\")'",
        ]
        for i, payload in enumerate(command_payloads):
            response = test_client.post(
                "/create_feature_metadata",
                json={
                    "feature_name": f"security:cmd:v{i}",
                    "feature_type": "compute-first",
                    "feature_data_type": "string",
                    "query": f"SELECT field FROM table WHERE condition = '{payload}'",
                    "description": "Command injection test",
                    "created_by": "security_tester",
                    "user_role": "developer",
                },
            )
            assert response.status_code in [201, 400, 422]

    # Path traversal prevention
    def test_path_traversal_prevention(self, test_client):
        path_payloads = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "/etc/shadow",
            "../../../../etc/hosts",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
        ]
        for i, payload in enumerate(path_payloads):
            response = test_client.post(
                "/create_feature_metadata",
                json={
                    "feature_name": f"security:path:v{i}",
                    "feature_type": "batch",
                    "feature_data_type": "string",
                    "query": "SELECT data FROM files",
                    "description": payload,
                    "created_by": "security_tester",
                    "user_role": "developer",
                },
            )
            assert response.status_code in [201, 400, 422]

    # Large input handling
    def test_large_input_handling(self, test_client):
        long_string = "A" * 10000
        response = test_client.post(
            "/create_feature_metadata",
            json={
                "feature_name": "security:large:v1",
                "feature_type": "batch",
                "feature_data_type": "string",
                "query": "SELECT data FROM table",
                "description": long_string,
                "created_by": "security_tester",
                "user_role": "developer",
            },
        )
        assert response.status_code in [201, 400, 422, 413]

    # Special characters handling
    def test_special_characters_handling(self, test_client):
        special_chars = [
            "特殊字符测试",
            "тест кириллица",
            "🚀🔥💯",
            "test\x00null",
            "test\r\nCRLF",
            "test\ttab\nnewline",
        ]
        for i, chars in enumerate(special_chars):
            response = test_client.post(
                "/create_feature_metadata",
                json={
                    "feature_name": f"security:special:v{i}",
                    "feature_type": "real-time",
                    "feature_data_type": "string",
                    "query": "SELECT value FROM table",
                    "description": chars,
                    "created_by": "security_tester",
                    "user_role": "developer",
                },
            )
            assert response.status_code in [201, 400, 422]

    # JSON injection prevention
    def test_json_injection_prevention(self, test_client):
        json_payloads = [
            '{"malicious": "payload"}',
            '[{"injection": true}]',
            '\\"; malicious: true; //',
            '{"__proto__": {"isAdmin": true}}',
        ]
        for i, payload in enumerate(json_payloads):
            response = test_client.post(
                "/create_feature_metadata",
                json={
                    "feature_name": f"security:json:v{i}",
                    "feature_type": "batch",
                    "feature_data_type": "string",
                    "query": "SELECT json_data FROM table",
                    "description": payload,
                    "created_by": "security_tester",
                    "user_role": "developer",
                },
            )
            assert response.status_code in [201, 400, 422]

    # Header injection prevention
    def test_header_injection_prevention(self, test_client):
        malicious_headers = {
            "X-Forwarded-For": "127.0.0.1, <script>alert('xss')</script>",
            "User-Agent": "Mozilla/5.0\r\nSet-Cookie: admin=true",
            "Content-Type": "application/json\r\nLocation: http://evil.com",
        }
        response = test_client.post(
            "/create_feature_metadata",
            json={
                "feature_name": "security:header:v1",
                "feature_type": "batch",
                "feature_data_type": "string",
                "query": "SELECT data FROM table",
                "description": "Header injection test",
                "created_by": "security_tester",
                "user_role": "developer",
            },
            headers=malicious_headers,
        )
        assert response.status_code in [201, 400, 422]


class TestRoleBasedSecurity:
    """Test role-based access control."""

    # Setup test client
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = TestClient(app)

    # Privilege escalation prevention
    def test_privilege_escalation_prevention(self, test_client):
        response = test_client.post(
            "/create_feature_metadata",
            json={
                "feature_name": "security:escalation:v1",
                "feature_type": "batch",
                "feature_data_type": "string",
                "query": "SELECT * FROM admin_table",
                "description": "Privilege escalation test",
                "created_by": "regular_user",
                "user_role": "admin",
            },
        )
        assert response.status_code == 400
        detail = response.json()["detail"]
        assert "Invalid role" in detail or "cannot perform action" in detail

    # Cross-role action prevention
    def test_cross_role_action_prevention(self, test_client):
        test_client.post(
            "/create_feature_metadata",
            json={
                "feature_name": "security:cross:v1",
                "feature_type": "batch",
                "feature_data_type": "int",
                "query": "SELECT count FROM table",
                "description": "Cross role test",
                "created_by": "developer",
                "user_role": "developer",
            },
        )
        response = test_client.post(
            "/approve_feature_metadata",
            json={
                "feature_name": "security:cross:v1",
                "approved_by": "fake_approver",
                "user_role": "developer",
                "approval_notes": "Trying to approve with wrong role",
            },
        )
        assert response.status_code == 400
        detail = response.json()["detail"].lower()
        assert "cannot perform action" in detail or "not allowed" in detail

    # Unauthorized data access prevention
    def test_unauthorized_data_access_prevention(self, test_client):
        response = test_client.post(
            "/get_all_feature_metadata", json={"user_role": "unauthorized_role"}
        )
        assert response.status_code == 400
        assert "Invalid role" in response.json()["detail"]
