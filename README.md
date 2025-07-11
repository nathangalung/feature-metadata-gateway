# Feature Metadata Gateway

## Quick Start

### Using Docker (Recommended)
```bash
# Start the application server
docker compose up app

# Run all tests
docker compose up test

# Development mode with hot reload
docker compose up dev
```

### Local Development
```bash
# Install dependencies with uv
uv sync

# Start development server
uv run uvicorn app.main:app --reload --port 8000

# Run tests with coverage
uv run pytest tests/ -v --cov=app --cov-report=term-missing

# Code quality checks
uv run ruff check app/ tests/
```

## Project Overview

### Architecture
```
feature-metadata-gateway/
├── app/                   # Main application
│   ├── main.py            # FastAPI endpoints
│   ├── models/            # Request/Response models
│   ├── services/          # Business logic & feature services
│   └── utils/             # Utility functions
├── tests/                 # Comprehensive test suite
├── data/                  # Feature metadata storage
├── .github/workflows/     # CI pipeline
└── docker-compose.yaml    # Container orchestration
```

### Key Features
- **CRUD Operations**: Create, Read, Update, Delete feature metadata
- **Status Hierarchy**: Controlled feature lifecycle management
- **Batch Processing**: Handle multiple features and entities
- **Feature Registry**: Centralized management of feature metadata
- **Deterministic Results**: Consistent feature values for testing
- **Health Monitoring**: Built-in health checks and feature listing
- **Comprehensive Testing**: 99%+ test coverage with edge cases
- **CI Pipeline**: Automated testing, linting, and Docker integration

## API Documentation

### Endpoints
| Method | Endpoint | Description | Example |
|--------|----------|-------------|---------|
| `GET` | `/health` | Health check | `{"status": "ok", "timestamp": 1751429485000}` |
| `GET` | `/features/available` | List available features | `{"available_features": ["driver_hourly_stats:conv_rate:1", ...]}` |
| `GET` | `/features/{feature_name}` | Get single feature metadata | Feature metadata object |
| `POST` | `/features` | Batch feature requests | See examples below |
| `POST` | `/features/create` | Create new feature | Feature creation response |
| `PUT` | `/features/{feature_name}` | Update feature metadata | Feature update response |
| `DELETE` | `/features/{feature_name}` | Delete feature metadata | Feature deletion response |

### Available Features
- `driver_hourly_stats:conv_rate:1` - Driver conversion rate (float)
- `driver_hourly_stats:acc_rate:2` - Driver acceptance rate (integer)
- `driver_hourly_stats:avg_daily_trips:3` - Average daily trips (string)
- `fraud:amount:v1` - Transaction amount for fraud detection (float)
- `customer:income:v1` - Customer income data (integer)

### Status Hierarchy
1. **READY FOR TESTING** - Initial development complete
2. **TESTED** - Validation testing passed
3. **APPROVED** - Ready for production use
4. **DEPLOYED** - Currently in production

## API Usage Examples

### Basic Feature Request
```bash
curl -X POST "http://localhost:8000/features" \
  -H "Content-Type: application/json" \
  -d '{
    "features": ["driver_hourly_stats:conv_rate:1"],
    "entities": {"cust_no": ["X123456"]},
    "event_timestamp": 1751429485000
  }'
```

### Multiple Features and Entities
```bash
curl -X POST "http://localhost:8000/features" \
  -H "Content-Type: application/json" \
  -d '{
    "features": ["driver_hourly_stats:conv_rate:1", "driver_hourly_stats:acc_rate:2"],
    "entities": {"cust_no": ["X123456", "1002"]},
    "event_timestamp": 1751429485000
  }'
```

### Create New Feature
```bash
curl -X POST "http://localhost:8000/features/create" \
  -H "Content-Type: application/json" \
  -d '{
    "feature_name": "new:feature:1",
    "feature_type": "real-time",
    "feature_data_type": "float",
    "query": "SELECT value FROM table WHERE id = ?",
    "created_by": "developer",
    "description": "New feature description"
  }'
```

### Update Feature Metadata
```bash
curl -X PUT "http://localhost:8000/features/new:feature:1" \
  -H "Content-Type: application/json" \
  -d '{
    "feature_type": "batch",
    "last_updated_by": "updater",
    "status": "TESTED",
    "description": "Updated description"
  }'
```

### Get Single Feature
```bash
curl -X GET "http://localhost:8000/features/driver_hourly_stats:conv_rate:1"
```

### Delete Feature
```bash
curl -X DELETE "http://localhost:8000/features/new:feature:1"
```

### Request Format
```json
{
  "features": ["driver_hourly_stats:conv_rate:1", "driver_hourly_stats:acc_rate:2"],
  "entities": {"cust_no": ["X123456", "1002"]},
  "event_timestamp": 1751429485000
}
```

### Response Format
```json
{
  "metadata": {
    "feature_names": ["cust_no", "driver_hourly_stats:conv_rate:1", "driver_hourly_stats:acc_rate:2"]
  },
  "results": [
    {
      "values": [
        "X123456",
        {
          "feature_type": "real-time",
          "feature_data_type": "float",
          "query": "SELECT conv_rate FROM driver_hourly_stats WHERE driver_id = ?",
          "created_time": 1751429485000,
          "updated_time": 1751429485000,
          "created_by": "Fia",
          "last_updated_by": "Ludy",
          "approved_by": "Endy",
          "status": "READY FOR TESTING",
          "description": "Conversion rate for driver"
        },
        {
          "feature_type": "batch",
          "feature_data_type": "integer",
          "query": "SELECT acc_rate FROM driver_hourly_stats WHERE driver_id = ?",
          "created_time": 1641081600000,
          "updated_time": 1751429485000,
          "created_by": "Ludy",
          "last_updated_by": "Eka",
          "approved_by": "Endy",
          "status": "APPROVED",
          "description": "Acceptance rate for driver"
        }
      ],
      "statuses": ["200 OK", "200 OK", "200 OK"],
      "event_timestamps": [1751429485000, 1751429485000, 1751429485000]
    }
  ]
}
```

## Feature Management

### Feature Status Hierarchy
Features progress through controlled status levels:

1. **READY FOR TESTING** - Initial development complete
2. **TESTED** - Validation testing passed
3. **APPROVED** - Ready for production use
4. **DEPLOYED** - Currently in production

### Status Transition Rules
- Features can only advance in hierarchy
- DEPLOYED status requires APPROVED status first
- APPROVED status requires TESTED status first
- Deployed features cannot be edited or deleted
- Status transitions require appropriate approvals

### Feature Format
Features follow the format: `category:name:version`
- `category`: Feature category (e.g., `driver_hourly_stats`)
- `name`: Feature name (e.g., `conv_rate`)
- `version`: Version number (e.g., `1`)

### Adding New Features
1. Use POST `/features/create` endpoint
2. Progress through status hierarchy
3. Obtain approvals for deployment
4. Update tests and documentation

## Testing

### Test Structure
```
tests/
├── test_main.py              # API endpoint tests
├── test_features.py          # Feature processing tests
├── test_services.py          # Service layer tests
├── test_models.py            # Data model tests
├── test_validation.py        # Input validation tests
├── test_health.py            # Health check tests
├── test_coverage.py          # Edge case coverage
├── test_comprehensive.py     # Integration tests
└── test_crud.py              # CRUD operation tests
```

### Running Tests
```bash
# Run all tests with coverage
uv run pytest tests/ -v --cov=app --cov-report=term-missing

# Run specific test files
uv run pytest tests/test_crud.py -v
uv run pytest tests/test_validation.py -v

# Run with detailed output
uv run pytest tests/ -v -s --tb=short
```

### Test Coverage: 99%+
- **Unit Tests**: Individual components
- **Integration Tests**: End-to-end workflows
- **CRUD Tests**: Create, Read, Update, Delete operations
- **Status Tests**: Feature lifecycle management
- **Performance Tests**: Load and response time
- **Edge Cases**: Error handling and boundaries
- **Validation Tests**: Request/response validation

## Docker Usage

### Build and Run
```bash
# Build the image
docker build -t feature-gateway .

# Run the container
docker run -p 8000:8000 feature-gateway

# Use docker compose for full setup
docker compose up app
```

### Container Features
- Health checks for orchestration
- Multi-stage build with uv package manager
- Optimized for production deployment
- CORS middleware enabled
- Persistent data storage

## Development

### Code Quality Tools
```bash
# Linting and formatting
uv run ruff check app/ tests/           # Fast linting
uv run black app/ tests/                # Code formatting
uv run isort app/ tests/                # Import sorting

# Type checking
uv run mypy app/                        # Static type checking
```

### Project Configuration
- **Python**: 3.13+
- **Package Manager**: uv (faster than pip)
- **Framework**: FastAPI + Uvicorn
- **Testing**: pytest with comprehensive fixtures
- **Linting**: ruff + black + isort
- **CI**: GitHub Actions

### Environment Setup
1. **Install uv**: `curl -LsSf https://astral.sh/uv/install.sh | sh`
2. **Clone repository**: `git clone <repo-url>`
3. **Install dependencies**: `uv sync`
4. **Start development**: `uv run uvicorn app.main:app --reload`

## Sample Data

### Feature Metadata (data/feature_metadata.json)
```json
{
  "fraud:amount:v1": {
    "feature_type": "real-time",
    "query": "SELECT amount FROM transactions WHERE id = ?",
    "created_time": 1640995200000,
    "updated_time": 1751429485000,
    "created_by": "data_engineer_1",
    "last_updated_by": "data_engineer_2",
    "feature_data_type": "float",
    "approved_by": "ml_engineer_1",
    "status": "DEPLOYED",
    "description": "Transaction amount for fraud detection"
  },
  "customer:income:v1": {
    "feature_type": "batch",
    "query": "SELECT income FROM customer_profile WHERE cust_id = ?",
    "created_time": 1641081600000,
    "updated_time": 1751429485000,
    "created_by": "data_scientist_1",
    "last_updated_by": "data_scientist_1",
    "feature_data_type": "integer",
    "approved_by": "ml_engineer_2",
    "status": "APPROVED",
    "description": "Customer annual income"
  }
}
```

## CI Pipeline

### GitHub Actions Workflow
- **Test Job**: Runs all tests with coverage reporting
- **Lint Job**: Code quality checks (ruff, black, isort)
- **Docker Test**: Build and test Docker image
- **Integration Test**: End-to-end testing with Docker Compose
- **CRUD Test**: Feature lifecycle management testing

### Pipeline Triggers
- Push to `main` or `develop` branches
- Pull requests to `main` branch
- Automated testing on every commit

## Performance

### Monitoring
```bash
# Health check
curl http://localhost:8000/health

# Available features
curl http://localhost:8000/features/available

# Docker health check
docker ps --format "table {{.Names}}\t{{.Status}}"
```

### Performance Characteristics
- **Response Time**: < 50ms for single feature requests
- **Throughput**: > 1000 requests/second
- **Memory Usage**: < 256MB base consumption
- **Concurrent Requests**: Supports async processing
- **CRUD Operations**: Optimized file-based persistence