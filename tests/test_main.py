from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


# Root endpoint test
def test_root():
    resp = client.get("/")
    assert resp.status_code == 200


# Health GET test
def test_health_get():
    resp = client.get("/health")
    assert resp.status_code == 200


# Health POST test
def test_health_post():
    resp = client.post("/health")
    assert resp.status_code == 200


# Create feature success
def test_create_feature_success():
    resp = client.post(
        "/create_feature_metadata",
        json={
            "feature_name": "main:success:v1",
            "feature_type": "batch",
            "feature_data_type": "float",
            "query": "SELECT 1",
            "description": "desc",
            "created_by": "dev",
            "user_role": "developer",
        },
    )
    assert resp.status_code == 201


# Duplicate feature test
def test_create_feature_duplicate():
    data = {
        "feature_name": "main:exists:v1",
        "feature_type": "batch",
        "feature_data_type": "float",
        "query": "SELECT 1",
        "description": "desc",
        "created_by": "dev",
        "user_role": "developer",
    }
    client.post("/create_feature_metadata", json=data)
    resp = client.post("/create_feature_metadata", json=data)
    assert resp.status_code == 400
    assert "detail" in resp.json()


# Invalid role test
def test_create_feature_invalid_role():
    resp = client.post(
        "/create_feature_metadata",
        json={
            "feature_name": "main:badrole:v1",
            "feature_type": "batch",
            "feature_data_type": "float",
            "query": "SELECT 1",
            "description": "desc",
            "created_by": "dev",
            "user_role": "invalid",
        },
    )
    assert resp.status_code in (400, 422)
    assert "detail" in resp.json()


# Invalid data test
def test_create_feature_invalid_data():
    resp = client.post(
        "/create_feature_metadata",
        json={
            "feature_name": "",
            "feature_type": "",
            "feature_data_type": "",
            "query": "",
            "description": "",
            "created_by": "",
            "user_role": "developer",
        },
    )
    assert resp.status_code in (400, 422)
    assert "detail" in resp.json()


# Unexpected exception test
def test_create_feature_unexpected_exception(monkeypatch):
    monkeypatch.setattr(
        "app.services.feature_service.FeatureMetadataService.create_feature_metadata",
        lambda self, x: (_ for _ in ()).throw(Exception("unexpected")),
    )
    resp = client.post(
        "/create_feature_metadata",
        json={
            "feature_name": "main:unexpected:v1",
            "feature_type": "batch",
            "feature_data_type": "float",
            "query": "SELECT 1",
            "description": "desc",
            "created_by": "dev",
            "user_role": "developer",
        },
    )
    assert resp.status_code == 500
    assert "detail" in resp.json()


# Validation error test
def test_create_feature_validation_error():
    resp = client.post(
        "/create_feature_metadata",
        json={
            "feature_name": 123,
            "feature_type": "batch",
            "feature_data_type": "float",
            "query": "SELECT 1",
            "description": "desc",
            "created_by": "dev",
            "user_role": "developer",
        },
    )
    assert resp.status_code == 422
    assert "detail" in resp.json()


# Value error test
def test_create_feature_value_error(monkeypatch):
    monkeypatch.setattr(
        "app.services.feature_service.FeatureMetadataService.create_feature_metadata",
        lambda self, x: (_ for _ in ()).throw(ValueError("bad value")),
    )
    resp = client.post(
        "/create_feature_metadata",
        json={
            "feature_name": "main:valueerror:v1",
            "feature_type": "batch",
            "feature_data_type": "float",
            "query": "SELECT 1",
            "description": "desc",
            "created_by": "dev",
            "user_role": "developer",
        },
    )
    assert resp.status_code == 400
    assert "detail" in resp.json()


# Get feature by string
def test_get_feature_metadata_str():
    data = {
        "feature_name": "main:getstr:v1",
        "feature_type": "batch",
        "feature_data_type": "float",
        "query": "SELECT 1",
        "description": "desc",
        "created_by": "dev",
        "user_role": "developer",
    }
    client.post("/create_feature_metadata", json=data)
    resp = client.post(
        "/get_feature_metadata",
        json={"features": "main:getstr:v1", "user_role": "developer"},
    )
    assert resp.status_code == 200


# Get feature by list
def test_get_feature_metadata_list():
    data = {
        "feature_name": "main:getlist:v1",
        "feature_type": "batch",
        "feature_data_type": "float",
        "query": "SELECT 1",
        "description": "desc",
        "created_by": "dev",
        "user_role": "developer",
    }
    client.post("/create_feature_metadata", json=data)
    resp = client.post(
        "/get_feature_metadata",
        json={"features": ["main:getlist:v1"], "user_role": "developer"},
    )
    assert resp.status_code == 200


# Invalid features type
def test_get_feature_metadata_invalid_type():
    resp = client.post(
        "/get_feature_metadata",
        json={"features": 123, "user_role": "developer"},
    )
    assert resp.status_code == 422
    assert "detail" in resp.json()


# Feature not found
def test_get_feature_metadata_not_found():
    resp = client.post(
        "/get_feature_metadata",
        json={"features": "main:notfound:v1", "user_role": "developer"},
    )
    assert resp.status_code == 404
    assert "detail" in resp.json()


# Batch error test
def test_get_feature_metadata_batch_error(monkeypatch):
    monkeypatch.setattr(
        "app.services.feature_service.FeatureMetadataService.get_feature_metadata",
        lambda self, x, y="developer": (_ for _ in ()).throw(ValueError("batch error")),
    )
    resp = client.post(
        "/get_feature_metadata",
        json={"features": ["main:batcherror:v1"], "user_role": "developer"},
    )
    assert resp.status_code == 200


# General error test
def test_get_feature_metadata_general_error(monkeypatch):
    monkeypatch.setattr(
        "app.services.feature_service.FeatureMetadataService.get_feature_metadata",
        lambda self, x, y="developer": (_ for _ in ()).throw(
            Exception("general error")
        ),
    )
    resp = client.post(
        "/get_feature_metadata",
        json={"features": "main:generalerror:v1", "user_role": "developer"},
    )
    assert resp.status_code == 500
    assert "detail" in resp.json()


# Get all features success
def test_get_all_features_success():
    data = {
        "feature_name": "main:getall:v1",
        "feature_type": "batch",
        "feature_data_type": "float",
        "query": "SELECT 1",
        "description": "desc",
        "created_by": "dev",
        "user_role": "developer",
    }
    client.post("/create_feature_metadata", json=data)
    resp = client.post("/get_all_feature_metadata", json={"user_role": "developer"})
    assert resp.status_code == 200


# Invalid role for all features
def test_get_all_features_invalid_role():
    resp = client.post("/get_all_feature_metadata", json={"user_role": "invalid"})
    assert resp.status_code == 400
    assert "detail" in resp.json()


# Service not initialized test
def test_get_all_features_service_not_initialized(monkeypatch):
    monkeypatch.setattr("app.main.feature_service", None)
    resp = client.post("/get_all_feature_metadata", json={"user_role": "developer"})
    assert resp.status_code == 200


# Value error for all features
def test_get_all_features_value_error(monkeypatch):
    monkeypatch.setattr(
        "app.services.feature_service.FeatureMetadataService.get_all_feature_metadata",
        lambda self, x, y=None: (_ for _ in ()).throw(ValueError("bad value")),
    )
    resp = client.post("/get_all_feature_metadata", json={"user_role": "developer"})
    assert resp.status_code == 400
    assert "detail" in resp.json()


# General error for all features
def test_get_all_features_general_error(monkeypatch):
    monkeypatch.setattr(
        "app.services.feature_service.FeatureMetadataService.get_all_feature_metadata",
        lambda self, x, y=None: (_ for _ in ()).throw(Exception("general error")),
    )
    resp = client.post("/get_all_feature_metadata", json={"user_role": "developer"})
    assert resp.status_code == 500
    assert "detail" in resp.json()


# Update feature success
def test_update_feature_success():
    data = {
        "feature_name": "main:update:v1",
        "feature_type": "batch",
        "feature_data_type": "float",
        "query": "SELECT 1",
        "description": "desc",
        "created_by": "dev",
        "user_role": "developer",
    }
    client.post("/create_feature_metadata", json=data)
    resp = client.post(
        "/update_feature_metadata",
        json={
            "feature_name": "main:update:v1",
            "description": "Updated desc",
            "last_updated_by": "dev",
            "user_role": "developer",
        },
    )
    assert resp.status_code == 200
    assert resp.json()["metadata"]["status"] == "DRAFT"


# Update feature not found
def test_update_feature_not_found():
    resp = client.post(
        "/update_feature_metadata",
        json={
            "feature_name": "main:notfound:v1",
            "description": "desc",
            "last_updated_by": "dev",
            "user_role": "developer",
        },
    )
    assert resp.status_code == 400
    assert "detail" in resp.json()


# Update feature service not initialized
def test_update_feature_service_not_initialized(monkeypatch):
    monkeypatch.setattr("app.main.feature_service", None)
    resp = client.post(
        "/update_feature_metadata",
        json={
            "feature_name": "main:notinit:v1",
            "description": "desc",
            "last_updated_by": "dev",
            "user_role": "developer",
        },
    )
    assert resp.status_code == 400
    assert "detail" in resp.json()


# Update feature value error
def test_update_feature_value_error(monkeypatch):
    monkeypatch.setattr(
        "app.services.feature_service.FeatureMetadataService.update_feature_metadata",
        lambda self, x: (_ for _ in ()).throw(ValueError("bad value")),
    )
    resp = client.post(
        "/update_feature_metadata",
        json={
            "feature_name": "main:valueerror:v1",
            "description": "desc",
            "last_updated_by": "dev",
            "user_role": "developer",
        },
    )
    assert resp.status_code == 400
    assert "detail" in resp.json()


# Update feature general error
def test_update_feature_general_error(monkeypatch):
    monkeypatch.setattr(
        "app.services.feature_service.FeatureMetadataService.update_feature_metadata",
        lambda self, x: (_ for _ in ()).throw(Exception("general error")),
    )
    resp = client.post(
        "/update_feature_metadata",
        json={
            "feature_name": "main:generalerror:v1",
            "description": "desc",
            "last_updated_by": "dev",
            "user_role": "developer",
        },
    )
    assert resp.status_code == 500
    assert "detail" in resp.json()


# Update feature missing fields
def test_update_feature_missing_fields():
    resp = client.post(
        "/update_feature_metadata",
        json={
            "feature_name": "main:updatefail:v1",
            "user_role": "developer",
        },
    )
    assert resp.status_code in (400, 422)
    assert "detail" in resp.json()


# Delete feature success
def test_delete_feature_success():
    data = {
        "feature_name": "main:delete:v1",
        "feature_type": "batch",
        "feature_data_type": "float",
        "query": "SELECT 1",
        "description": "desc",
        "created_by": "dev",
        "user_role": "developer",
    }
    client.post("/create_feature_metadata", json=data)
    resp = client.post(
        "/delete_feature_metadata",
        json={
            "feature_name": "main:delete:v1",
            "deleted_by": "dev",
            "user_role": "developer",
            "deletion_reason": "test",
        },
    )
    assert resp.status_code == 200


# Delete feature not found
def test_delete_feature_not_found():
    resp = client.post(
        "/delete_feature_metadata",
        json={
            "feature_name": "main:notfound:v1",
            "deleted_by": "dev",
            "user_role": "developer",
            "deletion_reason": "test",
        },
    )
    assert resp.status_code == 400
    assert "detail" in resp.json()


# Delete feature service not initialized
def test_delete_feature_service_not_initialized(monkeypatch):
    monkeypatch.setattr("app.main.feature_service", None)
    resp = client.post(
        "/delete_feature_metadata",
        json={
            "feature_name": "main:notinit:v1",
            "deleted_by": "dev",
            "user_role": "developer",
            "deletion_reason": "test",
        },
    )
    assert resp.status_code == 400
    assert "detail" in resp.json()


# Delete feature value error
def test_delete_feature_value_error(monkeypatch):
    monkeypatch.setattr(
        "app.services.feature_service.FeatureMetadataService.delete_feature_metadata",
        lambda self, x: (_ for _ in ()).throw(ValueError("bad value")),
    )
    resp = client.post(
        "/delete_feature_metadata",
        json={
            "feature_name": "main:valueerror:v1",
            "deleted_by": "dev",
            "user_role": "developer",
            "deletion_reason": "test",
        },
    )
    assert resp.status_code == 400
    assert "detail" in resp.json()


# Delete feature general error
def test_delete_feature_general_error(monkeypatch):
    monkeypatch.setattr(
        "app.services.feature_service.FeatureMetadataService.delete_feature_metadata",
        lambda self, x: (_ for _ in ()).throw(Exception("general error")),
    )
    resp = client.post(
        "/delete_feature_metadata",
        json={
            "feature_name": "main:generalerror:v1",
            "deleted_by": "dev",
            "user_role": "developer",
            "deletion_reason": "test",
        },
    )
    assert resp.status_code == 500
    assert "detail" in resp.json()


# Delete feature missing reason
def test_delete_feature_missing_reason():
    data = {
        "feature_name": "main:deletemissing:v1",
        "feature_type": "batch",
        "feature_data_type": "float",
        "query": "SELECT 1",
        "description": "desc",
        "created_by": "dev",
        "user_role": "developer",
    }
    client.post("/create_feature_metadata", json=data)
    resp = client.post(
        "/delete_feature_metadata",
        json={
            "feature_name": "main:deletemissing:v1",
            "deleted_by": "dev",
            "user_role": "developer",
        },
    )
    assert resp.status_code == 422
    assert "detail" in resp.json()


# Submit test feature success
def test_submit_test_feature_success():
    data = {
        "feature_name": "main:submit:v1",
        "feature_type": "batch",
        "feature_data_type": "float",
        "query": "SELECT 1",
        "description": "desc",
        "created_by": "dev",
        "user_role": "developer",
    }
    client.post("/create_feature_metadata", json=data)
    resp = client.post(
        "/submit_test_feature_metadata",
        json={
            "feature_name": "main:submit:v1",
            "submitted_by": "dev",
            "user_role": "developer",
        },
    )
    assert resp.status_code == 200
    assert resp.json()["metadata"]["status"] == "READY_FOR_TESTING"


# Submit test feature service not initialized
def test_submit_test_feature_service_not_initialized(monkeypatch):
    monkeypatch.setattr("app.main.feature_service", None)
    resp = client.post(
        "/submit_test_feature_metadata",
        json={
            "feature_name": "main:notinit:v1",
            "submitted_by": "dev",
            "user_role": "developer",
        },
    )
    assert resp.status_code == 400
    assert "detail" in resp.json()


# Submit test feature value error
def test_submit_test_feature_value_error(monkeypatch):
    monkeypatch.setattr(
        "app.services.feature_service.FeatureMetadataService.submit_test_feature_metadata",
        lambda self, x: (_ for _ in ()).throw(ValueError("bad value")),
    )
    resp = client.post(
        "/submit_test_feature_metadata",
        json={
            "feature_name": "main:valueerror:v1",
            "submitted_by": "dev",
            "user_role": "developer",
        },
    )
    assert resp.status_code == 400
    assert "detail" in resp.json()


# Submit test feature general error
def test_submit_test_feature_general_error(monkeypatch):
    monkeypatch.setattr(
        "app.services.feature_service.FeatureMetadataService.submit_test_feature_metadata",
        lambda self, x: (_ for _ in ()).throw(Exception("general error")),
    )
    resp = client.post(
        "/submit_test_feature_metadata",
        json={
            "feature_name": "main:generalerror:v1",
            "submitted_by": "dev",
            "user_role": "developer",
        },
    )
    assert resp.status_code == 500
    assert "detail" in resp.json()


# Test feature metadata success
def test_test_feature_metadata_success():
    data = {
        "feature_name": "main:testfeature:v1",
        "feature_type": "batch",
        "feature_data_type": "float",
        "query": "SELECT 1",
        "description": "desc",
        "created_by": "dev",
        "user_role": "developer",
    }
    client.post("/create_feature_metadata", json=data)
    client.post(
        "/submit_test_feature_metadata",
        json={
            "feature_name": "main:testfeature:v1",
            "submitted_by": "dev",
            "user_role": "developer",
        },
    )
    resp = client.post(
        "/test_feature_metadata",
        json={
            "feature_name": "main:testfeature:v1",
            "test_result": "TEST_SUCCEEDED",
            "tested_by": "test_system",
            "user_role": "tester",
        },
    )
    assert resp.status_code == 200
    assert resp.json()["metadata"]["status"] == "TEST_SUCCEEDED"


# Test feature metadata value error
def test_test_feature_metadata_value_error(monkeypatch):
    monkeypatch.setattr(
        "app.services.feature_service.FeatureMetadataService.test_feature_metadata",
        lambda self, x: (_ for _ in ()).throw(ValueError("bad value")),
    )
    resp = client.post(
        "/test_feature_metadata",
        json={
            "feature_name": "main:valueerror:v1",
            "test_result": "TEST_SUCCEEDED",
            "tested_by": "test_system",
            "user_role": "tester",
        },
    )
    assert resp.status_code == 400
    assert "detail" in resp.json()


# Test feature metadata general error
def test_test_feature_metadata_general_error(monkeypatch):
    monkeypatch.setattr(
        "app.services.feature_service.FeatureMetadataService.test_feature_metadata",
        lambda self, x: (_ for _ in ()).throw(Exception("general error")),
    )
    resp = client.post(
        "/test_feature_metadata",
        json={
            "feature_name": "main:generalerror:v1",
            "test_result": "TEST_SUCCEEDED",
            "tested_by": "test_system",
            "user_role": "tester",
        },
    )
    assert resp.status_code == 500
    assert "detail" in resp.json()


# Approve feature success
def test_approve_feature_success():
    data = {
        "feature_name": "main:approvefeature:v1",
        "feature_type": "batch",
        "feature_data_type": "float",
        "query": "SELECT 1",
        "description": "desc",
        "created_by": "dev",
        "user_role": "developer",
    }
    client.post("/create_feature_metadata", json=data)
    client.post(
        "/submit_test_feature_metadata",
        json={
            "feature_name": "main:approvefeature:v1",
            "submitted_by": "dev",
            "user_role": "developer",
        },
    )
    client.post(
        "/test_feature_metadata",
        json={
            "feature_name": "main:approvefeature:v1",
            "test_result": "TEST_SUCCEEDED",
            "tested_by": "test_system",
            "user_role": "tester",
        },
    )
    resp = client.post(
        "/approve_feature_metadata",
        json={
            "feature_name": "main:approvefeature:v1",
            "approved_by": "approver",
            "user_role": "approver",
        },
    )
    assert resp.status_code == 200
    assert resp.json()["metadata"]["status"] == "DEPLOYED"


# Approve feature service not initialized
def test_approve_feature_service_not_initialized(monkeypatch):
    monkeypatch.setattr("app.main.feature_service", None)
    resp = client.post(
        "/approve_feature_metadata",
        json={
            "feature_name": "main:notinit:v1",
            "approved_by": "approver",
            "user_role": "approver",
        },
    )
    assert resp.status_code == 400
    assert "detail" in resp.json()


# Approve feature value error
def test_approve_feature_value_error(monkeypatch):
    monkeypatch.setattr(
        "app.services.feature_service.FeatureMetadataService.approve_feature_metadata",
        lambda self, x: (_ for _ in ()).throw(ValueError("bad value")),
    )
    resp = client.post(
        "/approve_feature_metadata",
        json={
            "feature_name": "main:valueerror:v1",
            "approved_by": "approver",
            "user_role": "approver",
        },
    )
    assert resp.status_code == 400
    assert "detail" in resp.json()


# Approve feature general error
def test_approve_feature_general_error(monkeypatch):
    monkeypatch.setattr(
        "app.services.feature_service.FeatureMetadataService.approve_feature_metadata",
        lambda self, x: (_ for _ in ()).throw(Exception("general error")),
    )
    resp = client.post(
        "/approve_feature_metadata",
        json={
            "feature_name": "main:generalerror:v1",
            "approved_by": "approver",
            "user_role": "approver",
        },
    )
    assert resp.status_code == 500
    assert "detail" in resp.json()


# Reject feature success
def test_reject_feature_success():
    data = {
        "feature_name": "main:rejectfeature:v1",
        "feature_type": "batch",
        "feature_data_type": "float",
        "query": "SELECT 1",
        "description": "desc",
        "created_by": "dev",
        "user_role": "developer",
    }
    client.post("/create_feature_metadata", json=data)
    client.post(
        "/submit_test_feature_metadata",
        json={
            "feature_name": "main:rejectfeature:v1",
            "submitted_by": "dev",
            "user_role": "developer",
        },
    )
    client.post(
        "/test_feature_metadata",
        json={
            "feature_name": "main:rejectfeature:v1",
            "test_result": "TEST_SUCCEEDED",
            "tested_by": "test_system",
            "user_role": "tester",
        },
    )
    resp = client.post(
        "/reject_feature_metadata",
        json={
            "feature_name": "main:rejectfeature:v1",
            "rejected_by": "approver",
            "user_role": "approver",
            "rejection_reason": "Test failed",
        },
    )
    assert resp.status_code == 200
    assert resp.json()["metadata"]["status"] == "REJECTED"


# Reject feature service not initialized
def test_reject_feature_service_not_initialized(monkeypatch):
    monkeypatch.setattr("app.main.feature_service", None)
    resp = client.post(
        "/reject_feature_metadata",
        json={
            "feature_name": "main:notinit:v1",
            "rejected_by": "approver",
            "user_role": "approver",
            "rejection_reason": "fail",
        },
    )
    assert resp.status_code == 400
    assert "detail" in resp.json()


# Reject feature value error
def test_reject_feature_value_error(monkeypatch):
    monkeypatch.setattr(
        "app.services.feature_service.FeatureMetadataService.reject_feature_metadata",
        lambda self, x: (_ for _ in ()).throw(ValueError("bad value")),
    )
    resp = client.post(
        "/reject_feature_metadata",
        json={
            "feature_name": "main:valueerror:v1",
            "rejected_by": "approver",
            "user_role": "approver",
            "rejection_reason": "fail",
        },
    )
    assert resp.status_code == 400
    assert "detail" in resp.json()


# Reject feature general error
def test_reject_feature_general_error(monkeypatch):
    monkeypatch.setattr(
        "app.services.feature_service.FeatureMetadataService.reject_feature_metadata",
        lambda self, x: (_ for _ in ()).throw(Exception("general error")),
    )
    resp = client.post(
        "/reject_feature_metadata",
        json={
            "feature_name": "main:generalerror:v1",
            "rejected_by": "approver",
            "user_role": "approver",
            "rejection_reason": "fail",
        },
    )
    assert resp.status_code == 500
    assert "detail" in resp.json()


# Validation error handler test
def test_validation_error_handler():
    resp = client.post(
        "/create_feature_metadata",
        json={
            "feature_name": 123,
            "feature_type": "batch",
            "feature_data_type": "float",
            "query": "SELECT 1",
            "description": "desc",
            "created_by": "dev",
            "user_role": "developer",
        },
    )
    assert resp.status_code == 422
    assert "detail" in resp.json()


# Value error handler test
def test_value_error_handler():
    import asyncio

    from app.main import value_error_handler

    class DummyRequest:
        async def body(self):
            return b""

    req = DummyRequest()
    resp = asyncio.run(value_error_handler(req, ValueError("bad value")))
    assert resp.status_code == 400
    assert b"Bad Request" in resp.body


# General error handler test
def test_general_error_handler():
    import asyncio

    from app.main import general_exception_handler

    class DummyRequest:
        async def body(self):
            return b""

    req = DummyRequest()
    resp = asyncio.run(general_exception_handler(req, Exception("fail")))
    assert resp.status_code == 500
    assert b"Internal Server Error" in resp.body


# Create feature service not initialized
def test_create_feature_service_not_initialized(monkeypatch):
    monkeypatch.setattr("app.main.ensure_service", lambda: None)
    monkeypatch.setattr("app.main.feature_service", None)
    resp = client.post(
        "/create_feature_metadata",
        json={
            "feature_name": "main:notinit:v1",
            "feature_type": "batch",
            "feature_data_type": "float",
            "query": "SELECT 1",
            "description": "desc",
            "created_by": "dev",
            "user_role": "developer",
        },
    )
    assert resp.status_code == 500
    assert resp.json()["detail"] == "Internal server error"


# Get feature metadata service not initialized
def test_get_feature_metadata_service_not_initialized(monkeypatch):
    monkeypatch.setattr("app.main.ensure_service", lambda: None)
    monkeypatch.setattr("app.main.feature_service", None)
    resp = client.post(
        "/get_feature_metadata",
        json={"features": "main:notinit:v1", "user_role": "developer"},
    )
    assert resp.status_code == 500
    assert resp.json()["detail"] == "Internal server error"


# Get all feature metadata service not initialized
def test_get_all_feature_metadata_service_not_initialized(monkeypatch):
    monkeypatch.setattr("app.main.ensure_service", lambda: None)
    monkeypatch.setattr("app.main.feature_service", None)
    resp = client.post("/get_all_feature_metadata", json={"user_role": "developer"})
    assert resp.status_code == 500
    assert resp.json()["detail"] == "Service not initialized"


# Update feature metadata service not initialized
def test_update_feature_metadata_service_not_initialized(monkeypatch):
    monkeypatch.setattr("app.main.ensure_service", lambda: None)
    monkeypatch.setattr("app.main.feature_service", None)
    resp = client.post(
        "/update_feature_metadata",
        json={
            "feature_name": "main:notinit:v1",
            "description": "desc",
            "last_updated_by": "dev",
            "user_role": "developer",
        },
    )
    assert resp.status_code == 500
    assert resp.json()["detail"] == "Internal server error"


# Delete feature metadata service not initialized
def test_delete_feature_metadata_service_not_initialized(monkeypatch):
    monkeypatch.setattr("app.main.ensure_service", lambda: None)
    monkeypatch.setattr("app.main.feature_service", None)
    resp = client.post(
        "/delete_feature_metadata",
        json={
            "feature_name": "main:notinit:v1",
            "deleted_by": "dev",
            "user_role": "developer",
            "deletion_reason": "test",
        },
    )
    assert resp.status_code == 500
    assert resp.json()["detail"] == "Service not initialized"


# Submit test feature metadata service not initialized
def test_submit_test_feature_metadata_service_not_initialized(monkeypatch):
    monkeypatch.setattr("app.main.ensure_service", lambda: None)
    monkeypatch.setattr("app.main.feature_service", None)
    resp = client.post(
        "/submit_test_feature_metadata",
        json={
            "feature_name": "main:notinit:v1",
            "submitted_by": "dev",
            "user_role": "developer",
        },
    )
    assert resp.status_code == 500
    assert resp.json()["detail"] == "Internal server error"


# Test feature metadata service not initialized
def test_test_feature_metadata_service_not_initialized(monkeypatch):
    monkeypatch.setattr("app.main.ensure_service", lambda: None)
    monkeypatch.setattr("app.main.feature_service", None)
    resp = client.post(
        "/test_feature_metadata",
        json={
            "feature_name": "main:notinit:v1",
            "test_result": "TEST_SUCCEEDED",
            "tested_by": "test_system",
            "user_role": "tester",
        },
    )
    assert resp.status_code == 500
    assert resp.json()["detail"] == "Internal server error"


# Approve feature metadata service not initialized
def test_approve_feature_metadata_service_not_initialized(monkeypatch):
    monkeypatch.setattr("app.main.ensure_service", lambda: None)
    monkeypatch.setattr("app.main.feature_service", None)
    resp = client.post(
        "/approve_feature_metadata",
        json={
            "feature_name": "main:notinit:v1",
            "approved_by": "approver",
            "user_role": "approver",
        },
    )
    assert resp.status_code == 500
    assert resp.json()["detail"] == "Internal server error"


# Reject feature metadata service not initialized
def test_reject_feature_metadata_service_not_initialized(monkeypatch):
    monkeypatch.setattr("app.main.ensure_service", lambda: None)
    monkeypatch.setattr("app.main.feature_service", None)
    resp = client.post(
        "/reject_feature_metadata",
        json={
            "feature_name": "main:notinit:v1",
            "rejected_by": "approver",
            "user_role": "approver",
            "rejection_reason": "fail",
        },
    )
    assert resp.status_code == 500
    assert resp.json()["detail"] == "Internal server error"


# Invalid features type test
def test_get_feature_metadata_invalid_features_type():
    resp = client.post(
        "/get_feature_metadata",
        json={"features": 123, "user_role": "developer"},
    )
    assert resp.status_code == 422


# Delete feature metadata missing reason
def test_delete_feature_metadata_missing_reason():
    data = {
        "feature_name": "main:deletemissing:v1",
        "feature_type": "batch",
        "feature_data_type": "float",
        "query": "SELECT 1",
        "description": "desc",
        "created_by": "dev",
        "user_role": "developer",
    }
    client.post("/create_feature_metadata", json=data)
    resp = client.post(
        "/delete_feature_metadata",
        json={
            "feature_name": "main:deletemissing:v1",
            "deleted_by": "dev",
            "user_role": "developer",
        },
    )
    assert resp.status_code == 422


# Validation exception handler direct test
def test_validation_exception_handler_direct():
    import asyncio

    from pydantic import BaseModel, ValidationError

    from app.main import validation_exception_handler

    class DummyRequest:
        async def body(self):
            return b""

    class DummyModel(BaseModel):
        foo: int

    try:
        DummyModel(foo="bar")
    except ValidationError as exc:
        req = DummyRequest()
        resp = asyncio.run(validation_exception_handler(req, exc))
        assert resp.status_code == 422
        body = resp.body.decode()
        assert "Validation Error" in body
        assert "Request validation failed" in body


# Invalid features type runtime test
def test_get_feature_metadata_invalid_features_type_runtime():
    from fastapi import HTTPException

    from app.main import get_feature_metadata

    class DummyRequest:
        features = {"foo": "bar"}
        user_role = "developer"

    try:
        import asyncio

        asyncio.run(get_feature_metadata(DummyRequest()))
    except HTTPException as exc:
        assert exc.status_code == 500
        assert exc.detail == "Internal server error"


# Delete feature metadata empty reason
def test_delete_feature_metadata_empty_reason():
    data = {
        "feature_name": "main:deletemissing2:v1",
        "feature_type": "batch",
        "feature_data_type": "float",
        "query": "SELECT 1",
        "description": "desc",
        "created_by": "dev",
        "user_role": "developer",
    }
    client.post("/create_feature_metadata", json=data)
    resp = client.post(
        "/delete_feature_metadata",
        json={
            "feature_name": "main:deletemissing2:v1",
            "deleted_by": "dev",
            "user_role": "developer",
            "deletion_reason": "",
        },
    )
    assert resp.status_code == 422
    assert resp.json()["detail"] == "deletion_reason is required"
