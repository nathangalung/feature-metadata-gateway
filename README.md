# Feature Metadata Gateway

Production-ready FastAPI microservice for ML feature metadata management.

---

## Quick Start

### Docker usage

```bash
docker compose up --build
docker compose run feature-metadata-gateway-test
```

- App: [http://localhost:8000](http://localhost:8000)
- Health: [http://localhost:8000/health](http://localhost:8000/health)

### Local development

```bash
uv sync
uv run uvicorn app.main:app --reload --port 8000
uv run pytest tests/ -v --cov=app --cov-report=term-missing
```

---

## Project Structure

```
feature-metadata-gateway/
├── app/
│   ├── main.py
│   ├── models/
│   ├── services/
│   └── utils/
├── tests/
├── data/
├── Dockerfile
├── docker-compose.yaml
├── requirements.txt
├── pyproject.toml
└── README.md
```

---

## API Overview

All endpoints use JSON.

| Method | Endpoint                        | Description                        | Role Required               |
|--------|---------------------------------|------------------------------------|-----------------------------|
| GET    | `/health`                       | Health check                       | any                         |
| POST   | `/create_feature_metadata`      | Create feature                     | developer                   |
| POST   | `/get_feature_metadata`         | Get feature by name                | developer, approver, tester |
| POST   | `/get_all_feature_metadata`     | List features metadata (filter)    | developer, approver, tester |
| POST   | `/update_feature_metadata`      | Update feature                     | developer                   |
| POST   | `/delete_feature_metadata`      | Delete feature                     | developer                   |
| POST   | `/submit_test_feature_metadata` | Submit for testing                 | developer                   |
| POST   | `/test_feature_metadata`        | Record test result                 | tester                      |
| POST   | `/approve_feature_metadata`     | Approve and deploy                 | approver                    |
| POST   | `/reject_feature_metadata`      | Reject feature                     | approver                    |

---

## Feature Status Workflow

Feature lifecycle:

1. **DRAFT** → 2. **READY_FOR_TESTING** → 3. **TEST_SUCCEEDED**/**TEST_FAILED** → 4. **APPROVED**/**REJECTED** → 5. **DEPLOYED**

- **DRAFT**: Defining/fixing feature
- **READY_FOR_TESTING**: Submitted for testing
- **TEST_SUCCEEDED**: Passed tests
- **TEST_FAILED**: Failed tests
- **APPROVED**: Accepted after review
- **REJECTED**: Rejected after review
- **DEPLOYED**: Live and immutable

**Transitions:**
- Only forward transitions (except "reset" after failure/rejection)
- Deployed features cannot be edited or deleted

---

## Example Payloads

### Create Feature

```json
{
  "feature_name": "driver_hourly_stats:conv_rate:1",
  "feature_type": "batch",
  "feature_data_type": "float",
  "query": "SELECT conv_rate FROM driver_hourly_stats WHERE driver_id = ?",
  "description": "Conversion rate for driver",
  "created_by": "dev",
  "user_role": "developer"
}
```

### Get Feature Metadata

```json
{
  "features": "driver_hourly_stats:conv_rate:1",
  "user_role": "developer"
}
```

### List All Features Metadata

```json
{
  "user_role": "developer",
  "status": "DEPLOYED"
}
```

### Update Feature Metadata

```json
{
  "feature_name": "driver_hourly_stats:conv_rate:1",
  "last_updated_by": "dev",
  "user_role": "developer",
  "description": "Updated description"
}
```

### Delete Feature Metadata

```json
{
  "feature_name": "driver_hourly_stats:conv_rate:1",
  "deleted_by": "dev",
  "user_role": "developer",
  "deletion_reason": "No longer needed"
}
```

### Submit for Testing

```json
{
  "feature_name": "driver_hourly_stats:conv_rate:1",
  "submitted_by": "dev",
  "user_role": "developer"
}
```

### Record Test Result

```json
{
  "feature_name": "driver_hourly_stats:conv_rate:1",
  "test_result": "TEST_SUCCEEDED",
  "tested_by": "qa",
  "user_role": "tester"
}
```

### Approve Feature

```json
{
  "feature_name": "driver_hourly_stats:conv_rate:1",
  "approved_by": "approver",
  "user_role": "approver"
}
```

### Reject Feature

```json
{
  "feature_name": "driver_hourly_stats:conv_rate:1",
  "rejected_by": "approver",
  "user_role": "approver",
  "rejection_reason": "Test failed"
}
```

---

## Example Response

```json
{
  "message": "Feature metadata created successfully",
  "metadata": {
    "feature_name": "driver_hourly_stats:conv_rate:1",
    "feature_type": "batch",
    "feature_data_type": "float",
    "query": "SELECT conv_rate FROM driver_hourly_stats WHERE driver_id = ?",
    "description": "Conversion rate for driver",
    "status": "DRAFT",
    "created_time": 1751429485000,
    "updated_time": 1751429485000,
    "created_by": "dev"
  }
}
```

---

## Testing

- All endpoints covered by tests
- Run tests:
  ```bash
  uv run pytest tests/ -v --cov=app --cov-report=term-missing
  ```
- Status transitions fully tested

---

## CI/CD

- All pushes/PRs run tests and linting via GitHub Actions
- CI: `pytest`, `ruff`, `black`, `isort`, `mypy`, Docker build/test, security scans
- See `.github/workflows/ci.yml` for pipeline

---

## Docker Usage

```bash
docker compose up --build
```
- App: [http://localhost:8000](http://localhost:8000)
- Health: [http://localhost:8000/health](http://localhost:8000/health)

```bash
docker compose run feature-metadata-gateway-test
```

---

## Development

- Lint: `uv run ruff check app/ tests/`
- Format: `uv run black app/ tests/`
- Sort imports: `uv run isort app/ tests/`
- Type check: `uv run mypy app/`
- Test: `uv run pytest tests/ -v --cov=app --cov-report=term-missing`
- Security: `uv run bandit -r app/` and `uv run safety check`

---

## Sample Data

See `data/feature_metadata.json` for example feature metadata.

---