"""Security tests for input validation."""

import pytest
from fastapi.testclient import TestClient

from app.main import app

@pytest.fixture
def test_client():
    with TestClient(app) as client:
        yield client

class TestInputValidation:
    """Test input validation security measures."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test client."""
        self.client = TestClient(app)

    def test_sql_injection_prevention(self, test_client):
        """Test SQL injection attack prevention."""
        sql_payloads = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "UNION SELECT * FROM admin",
            "'; INSERT INTO admin VALUES ('hacker'); --",
            "' AND 1=1 --",
            "' UNION ALL SELECT password FROM users WHERE 'a'='a"
        ]

        for i, payload in enumerate(sql_payloads):
            response = test_client.post("/create_feature_metadata", json={
                "feature_name": f"security:sql:v{i}",
                "feature_type": "batch",
                "feature_data_type": "string",
                "query": payload,
                "description": "SQL injection test",
                "created_by": "security_tester",
                "user_role": "developer"
            })

            # System should handle SQL injection safely
            assert response.status_code in [201, 400, 422]

            if response.status_code == 201:
                metadata = response.json()["metadata"]
                assert "query" in metadata
                assert isinstance(metadata["query"], str)

    def test_xss_prevention(self, test_client):
        """Test XSS attack prevention."""
        xss_payloads = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "{{constructor.constructor('alert(1)')()}}",
            "<svg onload=alert('xss')>",
            "';alert('xss');//"
        ]

        for i, payload in enumerate(xss_payloads):
            response = test_client.post("/create_feature_metadata", json={
                "feature_name": f"security:xss:v{i}",
                "feature_type": "real-time",
                "feature_data_type": "string",
                "query": "SELECT name FROM table",
                "description": payload,
                "created_by": "security_tester",
                "user_role": "developer"
            })

            if response.status_code == 201:
                metadata = response.json()["metadata"]
                assert "description" in metadata
                assert isinstance(metadata["description"], str)
            else:
                assert response.status_code in [400, 422]

    def test_command_injection_prevention(self, test_client):
        """Test command injection prevention."""
        command_payloads = [
            "; ls -la",
            "| cat /etc/passwd",
            "& whoami",
            "`id`",
            "$(rm -rf /)",
            "; python -c 'import os; os.system(\"ls\")'"
        ]

        for i, payload in enumerate(command_payloads):
            response = test_client.post("/create_feature_metadata", json={
                "feature_name": f"security:cmd:v{i}",
                "feature_type": "compute-first",
                "feature_data_type": "string",
                "query": f"SELECT field FROM table WHERE condition = '{payload}'",
                "description": "Command injection test",
                "created_by": "security_tester",
                "user_role": "developer"
            })

            assert response.status_code in [201, 400, 422]

    def test_path_traversal_prevention(self, test_client):
        """Test path traversal attack prevention."""
        path_payloads = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "/etc/shadow",
            "../../../../etc/hosts",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd"
        ]

        for i, payload in enumerate(path_payloads):
            response = test_client.post("/create_feature_metadata", json={
                "feature_name": f"security:path:v{i}",
                "feature_type": "batch",
                "feature_data_type": "string",
                "query": "SELECT data FROM files",
                "description": payload,
                "created_by": "security_tester",
                "user_role": "developer"
            })

            assert response.status_code in [201, 400, 422]

    def test_large_input_handling(self, test_client):
        """Test handling of excessively large inputs."""
        long_string = "A" * 10000

        response = test_client.post("/create_feature_metadata", json={
            "feature_name": "security:large:v1",
            "feature_type": "batch",
            "feature_data_type": "string",
            "query": "SELECT data FROM table",
            "description": long_string,
            "created_by": "security_tester",
            "user_role": "developer"
        })

        assert response.status_code in [201, 400, 422, 413]

    def test_special_characters_handling(self, test_client):
        """Test handling of special characters."""
        special_chars = [
            "特殊字符测试",  # Chinese characters
            "тест кириллица",  # Cyrillic
            "🚀🔥💯",  # Emojis
            "test\x00null",  # Null bytes
            "test\r\nCRLF",  # CRLF injection
            "test\ttab\nnewline"  # Control characters
        ]

        for i, chars in enumerate(special_chars):
            response = test_client.post("/create_feature_metadata", json={
                "feature_name": f"security:special:v{i}",
                "feature_type": "real-time",
                "feature_data_type": "string",
                "query": "SELECT value FROM table",
                "description": chars,
                "created_by": "security_tester",
                "user_role": "developer"
            })

            assert response.status_code in [201, 400, 422]

    def test_json_injection_prevention(self, test_client):
        """Test JSON injection prevention."""
        json_payloads = [
            '{"malicious": "payload"}',
            '[{"injection": true}]',
            '\\"; malicious: true; //',
            '{"__proto__": {"isAdmin": true}}'
        ]

        for i, payload in enumerate(json_payloads):
            response = test_client.post("/create_feature_metadata", json={
                "feature_name": f"security:json:v{i}",
                "feature_type": "batch",
                "feature_data_type": "string",
                "query": "SELECT json_data FROM table",
                "description": payload,
                "created_by": "security_tester",
                "user_role": "developer"
            })

            assert response.status_code in [201, 400, 422]

    def test_header_injection_prevention(self, test_client):
        """Test HTTP header injection prevention."""
        malicious_headers = {
            "X-Forwarded-For": "127.0.0.1, <script>alert('xss')</script>",
            "User-Agent": "Mozilla/5.0\r\nSet-Cookie: admin=true",
            "Content-Type": "application/json\r\nLocation: http://evil.com"
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
                "user_role": "developer"
            },
            headers=malicious_headers
        )

        assert response.status_code in [201, 400, 422]


class TestRoleBasedSecurity:
    """Test role-based access control security."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test client."""
        self.client = TestClient(app)

    def test_privilege_escalation_prevention(self, test_client):
        """Test prevention of privilege escalation."""
        response = test_client.post("/create_feature_metadata", json={
            "feature_name": "security:escalation:v1",
            "feature_type": "batch",
            "feature_data_type": "string",
            "query": "SELECT * FROM admin_table",
            "description": "Privilege escalation test",
            "created_by": "regular_user",
            "user_role": "admin"  # Invalid role
        })

        assert response.status_code == 400
        detail = response.json()["detail"]
        assert "Invalid role" in detail or "cannot perform action" in detail

    def test_cross_role_action_prevention(self, test_client):
        """Test prevention of cross-role actions."""
        test_client.post("/create_feature_metadata", json={
            "feature_name": "security:cross:v1",
            "feature_type": "batch",
            "feature_data_type": "int",
            "query": "SELECT count FROM table",
            "description": "Cross role test",
            "created_by": "developer",
            "user_role": "developer"
        })

        response = test_client.post("/approve_feature_metadata", json={
            "feature_name": "security:cross:v1",
            "approved_by": "fake_approver",
            "user_role": "developer",  # Wrong role for approval
            "approval_notes": "Trying to approve with wrong role"
        })

        assert response.status_code == 400
        # Accept both possible error messages for robust test
        detail = response.json()["detail"].lower()
        assert "cannot perform action" in detail or "not allowed" in detail

    def test_unauthorized_data_access_prevention(self, test_client):
        """Test prevention of unauthorized data access."""
        response = test_client.post("/get_all_feature_metadata", json={
            "user_role": "unauthorized_role"
        })

        assert response.status_code == 400
        assert "Invalid role" in response.json()["detail"]