# Feature Metadata Gateway

A robust, production-ready FastAPI microservice for managing ML feature metadata, supporting the full feature lifecycle, batch retrieval, and deterministic feature value simulation. Designed for ML/DS feature stores, with comprehensive validation, status transitions, and CI/CD integration.

---

## Quick Start

### Using Docker (Recommended)

```bash
# Build and start the application server
docker compose up --build

# Run all tests in the container
docker compose run feature-metadata-gateway-test
```

### Local Development

```bash
# Install dependencies with uv
uv sync

# Start development server (hot reload)
uv run uvicorn app.main:app --reload --port 8000

# Run tests with coverage
uv run pytest tests/ -v --cov=app --cov-report=term-missing
```

---

## Project Structure

```
feature-metadata-gateway/
├── app/
│   ├── main.py            # FastAPI endpoints
│   ├── models/            # Request/Response models
│   ├── services/          # Business logic & feature services
│   └── utils/             # Utility functions
├── tests/                 # Comprehensive test suite (unit, integration, workflow, edge cases)
├── data/                  # Feature metadata storage (JSON)
├── Dockerfile
├── docker-compose.yaml
├── requirements.txt
├── pyproject.toml
└── README.md
```

---

## API Overview

All endpoints use JSON payloads. **All CRUD and workflow operations are POST endpoints** (except for a few GETs for health and listing).

### Endpoints

| Method | Endpoint                        | Description                        |
|--------|---------------------------------|------------------------------------|
| GET    | `/health`                       | Health check                       |
| POST   | `/create_feature_metadata`      | Create new feature                 |
| POST   | `/get_feature_metadata`         | Get feature metadata (by name)     |
| GET    | `/get_feature_metadata/{name}`  | Get feature metadata (by name)     |
| POST   | `/get_all_feature_metadata`     | List all features (with filters)   |
| GET    | `/get_all_feature_metadata`     | List all features (with filters)   |
| GET    | `/get_deployed_features`        | List deployed features             |
| GET    | `/features/available`           | List available features            |
| POST   | `/features`                     | Batch feature value retrieval      |
| POST   | `/update_feature_metadata`      | Update feature metadata            |
| POST   | `/delete_feature_metadata`      | Delete feature metadata            |
| POST   | `/ready_test_feature_metadata`  | Submit feature for testing         |
| POST   | `/test_feature_metadata`        | Record test result                 |
| POST   | `/approve_feature_metadata`     | Approve and deploy feature         |
| POST   | `/reject_feature_metadata`      | Reject feature                     |
| POST   | `/fix_feature_metadata`         | Fix and reset feature to draft     |

---

## Example Payloads

### Create Feature

**POST** `/create_feature_metadata`
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

**POST** `/get_feature_metadata`
```json
{
  "feature_name": "driver_hourly_stats:conv_rate:1",
  "user_role": "developer"
}
```

### List All Features (with filter)

**POST** `/get_all_feature_metadata`
```json
{
  "user_role": "developer",
  "status": "APPROVED"
}
```

### Batch Feature Value Retrieval

**POST** `/features`
```json
{
  "features": ["driver_hourly_stats:conv_rate:1", "driver_hourly_stats:acc_rate:2"],
  "entities": {"driver_id": ["D001", "D002"]},
  "event_timestamp": 1751429485000
}
```

### Update Feature Metadata

**POST** `/update_feature_metadata`
```json
{
  "feature_name": "driver_hourly_stats:conv_rate:1",
  "last_updated_by": "dev",
  "user_role": "developer",
  "description": "Updated description"
}
```

### Delete Feature Metadata

**POST** `/delete_feature_metadata`
```json
{
  "feature_name": "driver_hourly_stats:conv_rate:1",
  "deleted_by": "dev",
  "user_role": "developer",
  "deletion_reason": "No longer needed"
}
```

### Feature Workflow (Status Transitions)

**POST** `/ready_test_feature_metadata`
```json
{
  "feature_name": "driver_hourly_stats:conv_rate:1",
  "submitted_by": "dev",
  "user_role": "developer"
}
```
**POST** `/test_feature_metadata`
```json
{
  "feature_name": "driver_hourly_stats:conv_rate:1",
  "test_result": "TEST_SUCCEEDED",
  "tested_by": "qa",
  "user_role": "external_testing_system"
}
```
**POST** `/approve_feature_metadata`
```json
{
  "feature_name": "driver_hourly_stats:conv_rate:1",
  "approved_by": "approver",
  "user_role": "approver"
}
```
**POST** `/reject_feature_metadata`
```json
{
  "feature_name": "driver_hourly_stats:conv_rate:1",
  "rejected_by": "approver",
  "user_role": "approver",
  "rejection_reason": "Test failed"
}
```
**POST** `/fix_feature_metadata`
```json
{
  "feature_name": "driver_hourly_stats:conv_rate:1",
  "fixed_by": "dev",
  "user_role": "developer",
  "fix_description": "Fixed SQL bug"
}
```

---

## Example Response

```json
{
  "message": "Feature created successfully",
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

## Feature Status Hierarchy

1. **DRAFT** → 2. **READY_FOR_TESTING** → 3. **TEST_SUCCEEDED**/**TEST_FAILED** → 4. **APPROVED**/**REJECTED** → 5. **DEPLOYED**

- Only forward transitions allowed.
- Deployed features cannot be edited or deleted.

---

## Testing

- All endpoints are covered by tests in `tests/test_main.py` and related files.
- Run tests with:
  ```bash
  uv run pytest tests/ -v --cov=app --cov-report=term-missing
  ```

---

## Docker Usage

### Build and Run

```bash
docker compose up --build
```
- App will be available at [http://localhost:8000](http://localhost:8000)
- Health check: [http://localhost:8000/health](http://localhost:8000/health)

### Run Tests in Container

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

---

## CI/CD

- All pushes and PRs run tests and linting via GitHub Actions.
- CI checks: `pytest`, `ruff`, `black`, `isort`.

---

## Sample Data

See `data/feature_metadata.json` for example feature metadata.

---