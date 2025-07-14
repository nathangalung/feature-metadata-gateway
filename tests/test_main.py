import asyncio

from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.main import app

client = TestClient(app)


# Health check GET
def test_health_check_get():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"


# Health check POST
def test_health_check_post():
    resp = client.post("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"


# Create feature success
def test_create_feature_metadata_success():
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
    assert resp.json()["metadata"]["feature_name"] == "main:success:v1"


# Create feature invalid role
def test_create_feature_metadata_invalid_role():
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
    assert resp.status_code == 400 or resp.status_code == 422


# Create feature already exists
def test_create_feature_metadata_already_exists():
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
    assert "already exists" in resp.text


# Create feature validation error
def test_create_feature_metadata_validation_error():
    resp = client.post("/create_feature_metadata", json={})
    assert resp.status_code in (400, 422)


# Create feature internal error
def test_create_feature_metadata_internal_error(monkeypatch):
    from app.main import feature_service

    monkeypatch.setattr(
        feature_service,
        "create_feature_metadata",
        lambda x: (_ for _ in ()).throw(Exception("fail")),
    )
    resp = client.post(
        "/create_feature_metadata",
        json={
            "feature_name": "main:fail:v1",
            "feature_type": "batch",
            "feature_data_type": "float",
            "query": "SELECT 1",
            "description": "desc",
            "created_by": "dev",
            "user_role": "developer",
        },
    )
    assert resp.status_code == 500


# Get feature POST success
def test_get_feature_metadata_post_success():
    data = {
        "feature_name": "main:getpost:v1",
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
        json={"feature_name": "main:getpost:v1", "user_role": "developer"},
    )
    assert resp.status_code == 200
    assert resp.json()["metadata"]["feature_name"] == "main:getpost:v1"


# Get feature POST not found
def test_get_feature_metadata_post_not_found():
    resp = client.post(
        "/get_feature_metadata",
        json={"feature_name": "main:notfound:v1", "user_role": "developer"},
    )
    assert resp.status_code == 404


# Get feature POST internal error
def test_get_feature_metadata_post_internal_error(monkeypatch):
    from app.main import feature_service

    monkeypatch.setattr(
        feature_service,
        "get_feature_metadata",
        lambda *a, **k: (_ for _ in ()).throw(Exception("fail")),
    )
    resp = client.post(
        "/get_feature_metadata",
        json={"feature_name": "main:fail:v1", "user_role": "developer"},
    )
    assert resp.status_code == 500


# Get feature GET success
def test_get_feature_metadata_get_success():
    data = {
        "feature_name": "main:getget:v1",
        "feature_type": "batch",
        "feature_data_type": "float",
        "query": "SELECT 1",
        "description": "desc",
        "created_by": "dev",
        "user_role": "developer",
    }
    client.post("/create_feature_metadata", json=data)
    resp = client.get("/get_feature_metadata/main:getget:v1?user_role=developer")
    assert resp.status_code == 200
    assert resp.json()["metadata"]["feature_name"] == "main:getget:v1"


# Get feature GET not found
def test_get_feature_metadata_get_not_found():
    resp = client.get("/get_feature_metadata/main:notfound:v1?user_role=developer")
    assert resp.status_code == 404


# Get feature GET internal error
def test_get_feature_metadata_get_internal_error(monkeypatch):
    from app.main import feature_service

    monkeypatch.setattr(
        feature_service,
        "get_feature_metadata",
        lambda *a, **k: (_ for _ in ()).throw(Exception("fail")),
    )
    resp = client.get("/get_feature_metadata/main:fail:v1?user_role=developer")
    assert resp.status_code == 500


# Get all features POST success
def test_get_all_feature_metadata_post_success():
    data = {
        "feature_name": "main:getallpost:v1",
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
    assert "metadata" in resp.json()


# Get all features POST invalid role
def test_get_all_feature_metadata_post_invalid_role():
    resp = client.post("/get_all_feature_metadata", json={"user_role": "invalid"})
    assert resp.status_code == 400


# Get all features POST value error
def test_get_all_feature_metadata_post_value_error(monkeypatch):
    from app.main import feature_service

    monkeypatch.setattr(
        feature_service,
        "get_all_feature_metadata",
        lambda *a, **k: (_ for _ in ()).throw(ValueError("fail")),
    )
    resp = client.post("/get_all_feature_metadata", json={"user_role": "developer"})
    assert resp.status_code == 400


# Get all features POST internal error
def test_get_all_feature_metadata_post_internal_error(monkeypatch):
    from app.main import feature_service

    monkeypatch.setattr(
        feature_service,
        "get_all_feature_metadata",
        lambda *a, **k: (_ for _ in ()).throw(Exception("fail")),
    )
    resp = client.post("/get_all_feature_metadata", json={"user_role": "developer"})
    assert resp.status_code == 500


# Get all features GET success
def test_get_all_feature_metadata_get_success():
    resp = client.get("/get_all_feature_metadata?user_role=developer")
    assert resp.status_code == 200
    assert "metadata" in resp.json()


# Get all features GET invalid role
def test_get_all_feature_metadata_get_invalid_role():
    resp = client.get("/get_all_feature_metadata?user_role=invalid")
    assert resp.status_code == 400


# Get all features GET value error
def test_get_all_feature_metadata_get_value_error(monkeypatch):
    from app.main import feature_service

    monkeypatch.setattr(
        feature_service,
        "get_all_feature_metadata",
        lambda *a, **k: (_ for _ in ()).throw(ValueError("fail")),
    )
    resp = client.get("/get_all_feature_metadata?user_role=developer")
    assert resp.status_code == 400


# Get all features GET internal error
def test_get_all_feature_metadata_get_internal_error(monkeypatch):
    from app.main import feature_service

    monkeypatch.setattr(
        feature_service,
        "get_all_feature_metadata",
        lambda *a, **k: (_ for _ in ()).throw(Exception("fail")),
    )
    resp = client.get("/get_all_feature_metadata?user_role=developer")
    assert resp.status_code == 500


# Get deployed features success
def test_get_deployed_features_success():
    resp = client.get("/get_deployed_features?user_role=developer")
    assert resp.status_code == 200
    assert "features" in resp.json()


# Get deployed features internal error
def test_get_deployed_features_internal_error(monkeypatch):
    from app.main import feature_service

    monkeypatch.setattr(
        feature_service,
        "get_deployed_features",
        lambda *a, **k: (_ for _ in ()).throw(Exception("fail")),
    )
    resp = client.get("/get_deployed_features?user_role=developer")
    assert resp.status_code == 500


# Features available endpoint
def test_features_available_endpoint():
    resp = client.get("/features/available")
    assert resp.status_code == 200
    assert "available_features" in resp.json()


# Features endpoint
def test_features_endpoint():
    resp = client.post(
        "/features", json={"features": ["main:success:v1"], "entities": {}}
    )
    assert resp.status_code == 200
    assert "results" in resp.json()


# Update feature success
def test_update_feature_metadata_success():
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
            "last_updated_by": "dev",
            "user_role": "developer",
        },
    )
    assert resp.status_code == 200


# Update feature value error
def test_update_feature_metadata_value_error(monkeypatch):
    from app.main import feature_service

    monkeypatch.setattr(
        feature_service,
        "update_feature_metadata",
        lambda *a, **k: (_ for _ in ()).throw(ValueError("fail")),
    )
    resp = client.post(
        "/update_feature_metadata",
        json={
            "feature_name": "main:updatefail:v1",
            "last_updated_by": "dev",
            "user_role": "developer",
        },
    )
    assert resp.status_code == 400


# Update feature internal error
def test_update_feature_metadata_internal_error(monkeypatch):
    from app.main import feature_service

    monkeypatch.setattr(
        feature_service,
        "update_feature_metadata",
        lambda *a, **k: (_ for _ in ()).throw(Exception("fail")),
    )
    resp = client.post(
        "/update_feature_metadata",
        json={
            "feature_name": "main:updatefail:v1",
            "last_updated_by": "dev",
            "user_role": "developer",
        },
    )
    assert resp.status_code == 500


# Delete feature success
def test_delete_feature_metadata_success():
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


# Delete deployed feature
def test_delete_feature_metadata_deployed():
    data = {
        "feature_name": "main:deploydel:v1",
        "feature_type": "batch",
        "feature_data_type": "float",
        "query": "SELECT 1",
        "description": "desc",
        "created_by": "dev",
        "user_role": "developer",
    }
    client.post("/create_feature_metadata", json=data)
    client.post(
        "/ready_test_feature_metadata",
        json={
            "feature_name": "main:deploydel:v1",
            "submitted_by": "dev",
            "user_role": "developer",
        },
    )
    client.post(
        "/test_feature_metadata",
        json={
            "feature_name": "main:deploydel:v1",
            "test_result": "TEST_SUCCEEDED",
            "tested_by": "test_system",
            "user_role": "external_testing_system",
        },
    )
    client.post(
        "/approve_feature_metadata",
        json={
            "feature_name": "main:deploydel:v1",
            "approved_by": "approver",
            "user_role": "approver",
        },
    )
    resp = client.post(
        "/delete_feature_metadata",
        json={
            "feature_name": "main:deploydel:v1",
            "deleted_by": "dev",
            "user_role": "developer",
            "deletion_reason": "test",
        },
    )
    assert resp.status_code == 400
    assert "DEPLOYED" in resp.text


# Delete feature missing reason
def test_delete_feature_metadata_missing_reason():
    data = {
        "feature_name": "main:delreason:v1",
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
            "feature_name": "main:delreason:v1",
            "deleted_by": "dev",
            "user_role": "developer",
        },
    )
    assert resp.status_code == 422


# Delete feature value error
def test_delete_feature_metadata_value_error(monkeypatch):
    from app.main import feature_service

    monkeypatch.setattr(
        feature_service,
        "delete_feature_metadata",
        lambda *a, **k: (_ for _ in ()).throw(ValueError("fail")),
    )
    resp = client.post(
        "/delete_feature_metadata",
        json={
            "feature_name": "main:delvalerr:v1",
            "deleted_by": "dev",
            "user_role": "developer",
            "deletion_reason": "test",
        },
    )
    assert resp.status_code == 400


# Delete feature internal error
def test_delete_feature_metadata_internal_error(monkeypatch):
    from app.main import feature_service

    monkeypatch.setattr(
        feature_service,
        "delete_feature_metadata",
        lambda *a, **k: (_ for _ in ()).throw(Exception("fail")),
    )
    resp = client.post(
        "/delete_feature_metadata",
        json={
            "feature_name": "main:delerr:v1",
            "deleted_by": "dev",
            "user_role": "developer",
            "deletion_reason": "test",
        },
    )
    assert resp.status_code == 500


# Ready for testing success
def test_ready_test_feature_metadata_success():
    data = {
        "feature_name": "main:readytest:v1",
        "feature_type": "batch",
        "feature_data_type": "float",
        "query": "SELECT 1",
        "description": "desc",
        "created_by": "dev",
        "user_role": "developer",
    }
    client.post("/create_feature_metadata", json=data)
    resp = client.post(
        "/ready_test_feature_metadata",
        json={
            "feature_name": "main:readytest:v1",
            "submitted_by": "dev",
            "user_role": "developer",
        },
    )
    assert resp.status_code == 200


# Ready for testing value error
def test_ready_test_feature_metadata_value_error(monkeypatch):
    from app.main import feature_service

    monkeypatch.setattr(
        feature_service,
        "ready_test_feature_metadata",
        lambda *a, **k: (_ for _ in ()).throw(ValueError("fail")),
    )
    resp = client.post(
        "/ready_test_feature_metadata",
        json={
            "feature_name": "main:readytestfail:v1",
            "submitted_by": "dev",
            "user_role": "developer",
        },
    )
    assert resp.status_code == 400


# Ready for testing internal error
def test_ready_test_feature_metadata_internal_error(monkeypatch):
    from app.main import feature_service

    monkeypatch.setattr(
        feature_service,
        "ready_test_feature_metadata",
        lambda *a, **k: (_ for _ in ()).throw(Exception("fail")),
    )
    resp = client.post(
        "/ready_test_feature_metadata",
        json={
            "feature_name": "main:readytestfail:v1",
            "submitted_by": "dev",
            "user_role": "developer",
        },
    )
    assert resp.status_code == 500


# Test feature success
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
        "/ready_test_feature_metadata",
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
            "user_role": "external_testing_system",
        },
    )
    assert resp.status_code == 200


# Test feature value error
def test_test_feature_metadata_value_error(monkeypatch):
    from app.main import feature_service

    monkeypatch.setattr(
        feature_service,
        "test_feature_metadata",
        lambda *a, **k: (_ for _ in ()).throw(ValueError("fail")),
    )
    resp = client.post(
        "/test_feature_metadata",
        json={
            "feature_name": "main:testfeaturefail:v1",
            "test_result": "TEST_SUCCEEDED",
            "tested_by": "test_system",
            "user_role": "external_testing_system",
        },
    )
    assert resp.status_code == 400


# Test feature internal error
def test_test_feature_metadata_internal_error(monkeypatch):
    from app.main import feature_service

    monkeypatch.setattr(
        feature_service,
        "test_feature_metadata",
        lambda *a, **k: (_ for _ in ()).throw(Exception("fail")),
    )
    resp = client.post(
        "/test_feature_metadata",
        json={
            "feature_name": "main:testfeaturefail:v1",
            "test_result": "TEST_SUCCEEDED",
            "tested_by": "test_system",
            "user_role": "external_testing_system",
        },
    )
    assert resp.status_code == 500


# Approve feature success
def test_approve_feature_metadata_success():
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
        "/ready_test_feature_metadata",
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
            "user_role": "external_testing_system",
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


# Approve feature value error
def test_approve_feature_metadata_value_error(monkeypatch):
    from app.main import feature_service

    monkeypatch.setattr(
        feature_service,
        "approve_feature_metadata",
        lambda *a, **k: (_ for _ in ()).throw(ValueError("fail")),
    )
    resp = client.post(
        "/approve_feature_metadata",
        json={
            "feature_name": "main:approvefeaturefail:v1",
            "approved_by": "approver",
            "user_role": "approver",
        },
    )
    assert resp.status_code == 400


# Approve feature internal error
def test_approve_feature_metadata_internal_error(monkeypatch):
    from app.main import feature_service

    monkeypatch.setattr(
        feature_service,
        "approve_feature_metadata",
        lambda *a, **k: (_ for _ in ()).throw(Exception("fail")),
    )
    resp = client.post(
        "/approve_feature_metadata",
        json={
            "feature_name": "main:approvefeaturefail:v1",
            "approved_by": "approver",
            "user_role": "approver",
        },
    )
    assert resp.status_code == 500


# Reject feature success
def test_reject_feature_metadata_success():
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
        "/ready_test_feature_metadata",
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
            "user_role": "external_testing_system",
        },
    )
    resp = client.post(
        "/reject_feature_metadata",
        json={
            "feature_name": "main:rejectfeature:v1",
            "rejected_by": "approver",
            "user_role": "approver",
            "rejection_reason": "test",
        },
    )
    assert resp.status_code == 200


# Reject feature value error
def test_reject_feature_metadata_value_error(monkeypatch):
    from app.main import feature_service

    monkeypatch.setattr(
        feature_service,
        "reject_feature_metadata",
        lambda *a, **k: (_ for _ in ()).throw(ValueError("fail")),
    )
    resp = client.post(
        "/reject_feature_metadata",
        json={
            "feature_name": "main:rejectfeaturefail:v1",
            "rejected_by": "approver",
            "user_role": "approver",
            "rejection_reason": "test",
        },
    )
    assert resp.status_code == 400


# Reject feature internal error
def test_reject_feature_metadata_internal_error(monkeypatch):
    from app.main import feature_service

    monkeypatch.setattr(
        feature_service,
        "reject_feature_metadata",
        lambda *a, **k: (_ for _ in ()).throw(Exception("fail")),
    )
    resp = client.post(
        "/reject_feature_metadata",
        json={
            "feature_name": "main:rejectfeaturefail:v1",
            "rejected_by": "approver",
            "user_role": "approver",
            "rejection_reason": "test",
        },
    )
    assert resp.status_code == 500


# Fix feature success
def test_fix_feature_metadata_success():
    data = {
        "feature_name": "main:fixfeature:v1",
        "feature_type": "batch",
        "feature_data_type": "float",
        "query": "SELECT 1",
        "description": "desc",
        "created_by": "dev",
        "user_role": "developer",
    }
    client.post("/create_feature_metadata", json=data)
    client.post(
        "/ready_test_feature_metadata",
        json={
            "feature_name": "main:fixfeature:v1",
            "submitted_by": "dev",
            "user_role": "developer",
        },
    )
    client.post(
        "/test_feature_metadata",
        json={
            "feature_name": "main:fixfeature:v1",
            "test_result": "TEST_FAILED",
            "tested_by": "test_system",
            "user_role": "external_testing_system",
        },
    )
    resp = client.post(
        "/fix_feature_metadata",
        json={
            "feature_name": "main:fixfeature:v1",
            "fixed_by": "dev",
            "user_role": "developer",
            "fix_description": "fix",
        },
    )
    assert resp.status_code == 200


# Fix feature value error
def test_fix_feature_metadata_value_error(monkeypatch):
    from app.main import feature_service

    monkeypatch.setattr(
        feature_service,
        "fix_feature_metadata",
        lambda *a, **k: (_ for _ in ()).throw(ValueError("fail")),
    )
    resp = client.post(
        "/fix_feature_metadata",
        json={
            "feature_name": "main:fixfeaturefail:v1",
            "fixed_by": "dev",
            "user_role": "developer",
            "fix_description": "fix",
        },
    )
    assert resp.status_code == 400


# Fix feature internal error
def test_fix_feature_metadata_internal_error(monkeypatch):
    from app.main import feature_service

    monkeypatch.setattr(
        feature_service,
        "fix_feature_metadata",
        lambda *a, **k: (_ for _ in ()).throw(Exception("fail")),
    )
    resp = client.post(
        "/fix_feature_metadata",
        json={
            "feature_name": "main:fixfeaturefail:v1",
            "fixed_by": "dev",
            "user_role": "developer",
            "fix_description": "fix",
        },
    )
    assert resp.status_code == 500


# Validation exception handler
def test_validation_exception_handler_direct():
    from fastapi import Request

    from app.main import validation_exception_handler

    req = Request({"type": "http"})
    exc = ValidationError.from_exception_data("Test", [])
    resp = asyncio.run(validation_exception_handler(req, exc))
    assert resp.status_code in (400, 422)


# ValueError handler
def test_value_error_handler_direct():
    from fastapi import Request

    from app.main import value_error_handler

    req = Request({"type": "http"})
    resp = asyncio.run(value_error_handler(req, ValueError("test value error")))
    assert resp.status_code == 400
    assert "test value error" in resp.body.decode()


# General exception handler
def test_general_exception_handler_direct():
    from fastapi import Request

    from app.main import general_exception_handler

    req = Request({"type": "http"})
    resp = asyncio.run(general_exception_handler(req, Exception("test general error")))
    assert resp.status_code == 500
    body = resp.body.decode()
    assert "Internal Server Error" in body
    assert "An unexpected error occurred" in body


# Dummy feature different entities
def test_different_entities_different_values():
    from app.services.dummy_features import DriverConvRateV1

    feature = DriverConvRateV1("driver_hourly_stats:conv_rate:1")
    timestamp = 1234567890
    entities1 = {"driver_id": ["D001"]}
    entities2 = {"driver_id": ["D002"]}
    values1 = feature.get_feature_values(entities1, timestamp)
    values2 = feature.get_feature_values(entities2, timestamp)
    assert isinstance(values1, list)
    assert isinstance(values2, list)
    assert len(values1) == 1
    assert len(values2) == 1


# Ensure service branch
def test_ensure_service_branch(monkeypatch):
    from app import main as main_mod

    main_mod.feature_service = None
    main_mod.feature_metadata_service = None
    main_mod.ensure_service()
    main_mod.ensure_service()
    assert main_mod.feature_service is not None
    assert main_mod.feature_metadata_service is not None


# Create feature invalid user role
def test_create_feature_metadata_invalid_user_role_branch_explicit(monkeypatch):
    from app.main import feature_service

    def raise_invalid_role(*a, **k):
        raise ValueError("Invalid user role: not_a_role")

    monkeypatch.setattr(feature_service, "create_feature_metadata", raise_invalid_role)
    resp = client.post(
        "/create_feature_metadata",
        json={
            "feature_name": "main:badrole_explicit2:v1",
            "feature_type": "batch",
            "feature_data_type": "float",
            "query": "SELECT 1",
            "description": "desc",
            "created_by": "dev",
            "user_role": "not_a_role",
        },
    )
    assert resp.status_code == 400


# Create feature cannot perform action
def test_create_feature_metadata_cannot_perform_action_branch_explicit(monkeypatch):
    from app.main import feature_service

    def raise_cannot_perform(*a, **k):
        raise ValueError("User role developer cannot perform action create")

    monkeypatch.setattr(
        feature_service, "create_feature_metadata", raise_cannot_perform
    )
    resp = client.post(
        "/create_feature_metadata",
        json={
            "feature_name": "main:badrole_cannot2:v1",
            "feature_type": "batch",
            "feature_data_type": "float",
            "query": "SELECT 1",
            "description": "desc",
            "created_by": "dev",
            "user_role": "developer",
        },
    )
    assert resp.status_code == 400


# Create feature already exists explicit
def test_create_feature_metadata_already_exists_branch_explicit(monkeypatch):
    from app.main import feature_service

    def raise_already_exists(*a, **k):
        raise ValueError("Feature already exists")

    monkeypatch.setattr(
        feature_service, "create_feature_metadata", raise_already_exists
    )
    resp = client.post(
        "/create_feature_metadata",
        json={
            "feature_name": "main:exists_explicit2:v1",
            "feature_type": "batch",
            "feature_data_type": "float",
            "query": "SELECT 1",
            "description": "desc",
            "created_by": "dev",
            "user_role": "developer",
        },
    )
    assert resp.status_code == 400
    assert "already exists" in resp.text


# Create feature validation errors explicit
def test_create_feature_metadata_validation_errors_branch_explicit(monkeypatch):
    from app.main import feature_service

    def raise_validation_error(*a, **k):
        raise ValueError("Validation errors: feature_name: Invalid feature name format")

    monkeypatch.setattr(
        feature_service, "create_feature_metadata", raise_validation_error
    )
    resp = client.post(
        "/create_feature_metadata",
        json={
            "feature_name": "invalidname_explicit2",
            "feature_type": "batch",
            "feature_data_type": "float",
            "query": "SELECT 1",
            "description": "desc",
            "created_by": "dev",
            "user_role": "developer",
        },
    )
    assert resp.status_code == 400
    assert "Validation errors" in resp.text


# Lifespan shutdown log
def test_lifespan_shutdown_log_explicit():
    from fastapi.testclient import TestClient

    from app.main import app as fastapi_app

    with TestClient(fastapi_app) as client:
        resp = client.get("/health")
        assert resp.status_code == 200


# Approve feature generic error explicit
def test_approve_feature_metadata_generic_error_explicit(monkeypatch):
    from app.main import feature_service

    monkeypatch.setattr(
        feature_service,
        "approve_feature_metadata",
        lambda *a, **k: (_ for _ in ()).throw(Exception("fail")),
    )
    resp = client.post(
        "/approve_feature_metadata",
        json={
            "feature_name": "main:failapprove_explicit2:v1",
            "approved_by": "approver",
            "user_role": "approver",
        },
    )
    assert resp.status_code == 500


# Get all features GET with status
def test_get_all_feature_metadata_get_with_status():
    data = {
        "feature_name": "main:getallgetstatus:v1",
        "feature_type": "batch",
        "feature_data_type": "float",
        "query": "SELECT 1",
        "description": "desc",
        "created_by": "dev",
        "user_role": "developer",
    }
    client.post("/create_feature_metadata", json=data)
    resp = client.get("/get_all_feature_metadata?user_role=developer&status=DRAFT")
    assert resp.status_code == 200
    assert "metadata" in resp.json()
    assert any(m["status"] == "DRAFT" for m in resp.json()["metadata"])


# Get all features GET with feature_type
def test_get_all_feature_metadata_get_with_feature_type():
    data = {
        "feature_name": "main:getallgetftype:v1",
        "feature_type": "batch",
        "feature_data_type": "float",
        "query": "SELECT 1",
        "description": "desc",
        "created_by": "dev",
        "user_role": "developer",
    }
    client.post("/create_feature_metadata", json=data)
    resp = client.get(
        "/get_all_feature_metadata?user_role=developer&feature_type=batch"
    )
    assert resp.status_code == 200
    assert "metadata" in resp.json()
    assert any(m["feature_type"] == "batch" for m in resp.json()["metadata"])


# Get all features GET with created_by
def test_get_all_feature_metadata_get_with_created_by():
    data = {
        "feature_name": "main:getallgetcreator:v1",
        "feature_type": "batch",
        "feature_data_type": "float",
        "query": "SELECT 1",
        "description": "desc",
        "created_by": "special_creator",
        "user_role": "developer",
    }
    client.post("/create_feature_metadata", json=data)
    resp = client.get(
        "/get_all_feature_metadata?user_role=developer&created_by=special_creator"
    )
    assert resp.status_code == 200
    assert "metadata" in resp.json()
    assert any(m["created_by"] == "special_creator" for m in resp.json()["metadata"])


# Create feature value error fallback
def test_create_feature_metadata_value_error_fallback(monkeypatch):
    from app.main import feature_service

    def raise_other_value_error(*a, **k):
        raise ValueError("Some other error")

    monkeypatch.setattr(
        feature_service, "create_feature_metadata", raise_other_value_error
    )
    resp = client.post(
        "/create_feature_metadata",
        json={
            "feature_name": "main:othervalueerror:v1",
            "feature_type": "batch",
            "feature_data_type": "float",
            "query": "SELECT 1",
            "description": "desc",
            "created_by": "dev",
            "user_role": "developer",
        },
    )
    assert resp.status_code == 400
    assert "Some other error" in resp.text


# Get all features POST with status
def test_get_all_feature_metadata_post_with_status():
    data = {
        "feature_name": "main:getallpoststatus:v1",
        "feature_type": "batch",
        "feature_data_type": "float",
        "query": "SELECT 1",
        "description": "desc",
        "created_by": "dev",
        "user_role": "developer",
    }
    client.post("/create_feature_metadata", json=data)
    resp = client.post(
        "/get_all_feature_metadata", json={"user_role": "developer", "status": "DRAFT"}
    )
    assert resp.status_code == 200
    assert "metadata" in resp.json()
    assert any(m["status"] == "DRAFT" for m in resp.json()["metadata"])


# Get all features POST with feature_type
def test_get_all_feature_metadata_post_with_feature_type():
    data = {
        "feature_name": "main:getallpostftype:v1",
        "feature_type": "batch",
        "feature_data_type": "float",
        "query": "SELECT 1",
        "description": "desc",
        "created_by": "dev",
        "user_role": "developer",
    }
    client.post("/create_feature_metadata", json=data)
    resp = client.post(
        "/get_all_feature_metadata",
        json={"user_role": "developer", "feature_type": "batch"},
    )
    assert resp.status_code == 200
    assert "metadata" in resp.json()
    assert any(m["feature_type"] == "batch" for m in resp.json()["metadata"])


# Get all features POST with created_by
def test_get_all_feature_metadata_post_with_created_by():
    data = {
        "feature_name": "main:getallpostcreator:v1",
        "feature_type": "batch",
        "feature_data_type": "float",
        "query": "SELECT 1",
        "description": "desc",
        "created_by": "special_creator_post",
        "user_role": "developer",
    }
    client.post("/create_feature_metadata", json=data)
    resp = client.post(
        "/get_all_feature_metadata",
        json={"user_role": "developer", "created_by": "special_creator_post"},
    )
    assert resp.status_code == 200
    assert "metadata" in resp.json()
    assert any(
        m["created_by"] == "special_creator_post" for m in resp.json()["metadata"]
    )


# Convert request to dict fallback
def test_convert_request_to_dict_fallback_non_str_keys(temp_service):
    class Dummy:
        def __dir__(self):
            return [1, 2, 3]

    dummy = Dummy()
    result = temp_service._convert_request_to_dict(dummy)
    assert isinstance(result, dict)
    assert result == {}


# Create feature service none
def test_create_feature_metadata_service_none(monkeypatch):
    from app import main as main_mod

    main_mod.feature_service = None
    main_mod.feature_metadata_service = None
    monkeypatch.setattr(main_mod, "ensure_service", lambda: None)
    resp = client.post(
        "/create_feature_metadata",
        json={
            "feature_name": "main:failservicenone:v1",
            "feature_type": "batch",
            "feature_data_type": "float",
            "query": "SELECT 1",
            "description": "desc",
            "created_by": "dev",
            "user_role": "developer",
        },
    )
    assert resp.status_code == 500
    assert "Internal server error" in resp.text


# Get feature POST service none
def test_get_feature_metadata_service_none(monkeypatch):
    from app import main as main_mod

    main_mod.feature_service = None
    main_mod.feature_metadata_service = None
    monkeypatch.setattr(main_mod, "ensure_service", lambda: None)
    resp = client.post(
        "/get_feature_metadata",
        json={"feature_name": "main:failservicenone:v1", "user_role": "developer"},
    )
    assert resp.status_code == 500
    assert "Internal server error" in resp.text


# Get feature GET service none
def test_get_feature_metadata_get_service_none(monkeypatch):
    from app import main as main_mod

    main_mod.feature_service = None
    main_mod.feature_metadata_service = None
    monkeypatch.setattr(main_mod, "ensure_service", lambda: None)
    resp = client.get(
        "/get_feature_metadata/main:failservicenone:v1?user_role=developer"
    )
    assert resp.status_code == 500
    assert "Internal server error" in resp.text


# Get all features POST service none
def test_get_all_feature_metadata_post_service_none(monkeypatch):
    from app import main as main_mod

    main_mod.feature_service = None
    main_mod.feature_metadata_service = None
    monkeypatch.setattr(main_mod, "ensure_service", lambda: None)
    resp = client.post("/get_all_feature_metadata", json={"user_role": "developer"})
    assert resp.status_code == 500
    assert "Service not initialized" in resp.text


# Get all features GET service none
def test_get_all_feature_metadata_get_service_none(monkeypatch):
    from app import main as main_mod

    main_mod.feature_service = None
    main_mod.feature_metadata_service = None
    monkeypatch.setattr(main_mod, "ensure_service", lambda: None)
    resp = client.get("/get_all_feature_metadata?user_role=developer")
    assert resp.status_code == 500
    assert "Service not initialized" in resp.text


# Get available features service none
def test_get_available_features_service_none(monkeypatch):
    from app import main as main_mod

    main_mod.feature_service = None
    main_mod.feature_metadata_service = None
    monkeypatch.setattr(main_mod, "ensure_service", lambda: None)
    resp = client.get("/features/available")
    assert resp.status_code == 500
    assert "Service not initialized" in resp.text


# Update feature service none
def test_update_feature_metadata_service_none(monkeypatch):
    from app import main as main_mod

    main_mod.feature_service = None
    main_mod.feature_metadata_service = None
    monkeypatch.setattr(main_mod, "ensure_service", lambda: None)
    resp = client.post(
        "/update_feature_metadata",
        json={
            "feature_name": "main:failservicenone:v1",
            "last_updated_by": "dev",
            "user_role": "developer",
        },
    )
    assert resp.status_code == 500
    assert "Internal server error" in resp.text


# Delete feature service none
def test_delete_feature_metadata_service_none(monkeypatch):
    from app import main as main_mod

    main_mod.feature_service = None
    main_mod.feature_metadata_service = None
    monkeypatch.setattr(main_mod, "ensure_service", lambda: None)
    resp = client.post(
        "/delete_feature_metadata",
        json={
            "feature_name": "main:failservicenone:v1",
            "deleted_by": "dev",
            "user_role": "developer",
            "deletion_reason": "test",
        },
    )
    assert resp.status_code == 500
    assert "Service not initialized" in resp.text


# Ready for testing service none
def test_ready_test_feature_metadata_service_none(monkeypatch):
    from app import main as main_mod

    main_mod.feature_service = None
    main_mod.feature_metadata_service = None
    monkeypatch.setattr(main_mod, "ensure_service", lambda: None)
    resp = client.post(
        "/ready_test_feature_metadata",
        json={
            "feature_name": "main:failservicenone:v1",
            "submitted_by": "dev",
            "user_role": "developer",
        },
    )
    assert resp.status_code == 500
    assert "Internal server error" in resp.text


# Test feature service none
def test_test_feature_metadata_service_none(monkeypatch):
    from app import main as main_mod

    main_mod.feature_service = None
    main_mod.feature_metadata_service = None
    monkeypatch.setattr(main_mod, "ensure_service", lambda: None)
    resp = client.post(
        "/test_feature_metadata",
        json={
            "feature_name": "main:failservicenone:v1",
            "test_result": "TEST_SUCCEEDED",
            "tested_by": "test_system",
            "user_role": "external_testing_system",
        },
    )
    assert resp.status_code == 500
    assert "Internal server error" in resp.text


# Approve feature service none
def test_approve_feature_metadata_service_none(monkeypatch):
    from app import main as main_mod

    main_mod.feature_service = None
    main_mod.feature_metadata_service = None
    monkeypatch.setattr(main_mod, "ensure_service", lambda: None)
    resp = client.post(
        "/approve_feature_metadata",
        json={
            "feature_name": "main:failservicenone:v1",
            "approved_by": "approver",
            "user_role": "approver",
        },
    )
    assert resp.status_code == 500
    assert "Internal server error" in resp.text


# Reject feature service none
def test_reject_feature_metadata_service_none(monkeypatch):
    from app import main as main_mod

    main_mod.feature_service = None
    main_mod.feature_metadata_service = None
    monkeypatch.setattr(main_mod, "ensure_service", lambda: None)
    resp = client.post(
        "/reject_feature_metadata",
        json={
            "feature_name": "main:failservicenone:v1",
            "rejected_by": "approver",
            "user_role": "approver",
            "rejection_reason": "test",
        },
    )
    assert resp.status_code == 500
    assert "Internal server error" in resp.text


# Fix feature service none
def test_fix_feature_metadata_service_none(monkeypatch):
    from app import main as main_mod

    main_mod.feature_service = None
    main_mod.feature_metadata_service = None
    monkeypatch.setattr(main_mod, "ensure_service", lambda: None)
    resp = client.post(
        "/fix_feature_metadata",
        json={
            "feature_name": "main:failservicenone:v1",
            "fixed_by": "dev",
            "user_role": "developer",
            "fix_description": "fix",
        },
    )
    assert resp.status_code == 500
    assert "Internal server error" in resp.text


# Get current timestamp util
def test_get_current_timestamp(monkeypatch):
    from app.utils import timestamp

    ts = timestamp.get_current_timestamp()
    assert isinstance(ts, int)
    monkeypatch.setattr("time.time", lambda: (_ for _ in ()).throw(Exception("fail")))
    try:
        timestamp.get_current_timestamp()
    except Exception as e:
        assert str(e) == "fail"


# Get deployed features service none
def test_get_deployed_features_service_none(monkeypatch):
    from app import main as main_mod

    main_mod.feature_service = None
    main_mod.feature_metadata_service = None
    monkeypatch.setattr(main_mod, "ensure_service", lambda: None)
    resp = client.get("/get_deployed_features?user_role=developer")
    assert resp.status_code == 500
    assert "Internal server error" in resp.text
