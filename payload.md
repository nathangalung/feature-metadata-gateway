# API Payload Examples

## Read/Retrieve Features (Multiple)

### Request
```json
{
  "features": [
    "driver_hourly_stats:conv_rate:1", 
    "driver_hourly_stats:acc_rate:2", 
    "driver_hourly_stats:avg_daily_trips:3"
  ]
}
```

### Response
```json
{
  "metadata": {
    "features": [
      "driver_hourly_stats:conv_rate:1",
      "driver_hourly_stats:acc_rate:2", 
      "driver_hourly_stats:avg_daily_trips:3"
    ]
  },
  "results": {
    "values":[
        {
            "feature_type": "real-time",
            "feature_data_type": "float",
            "query": "SELECT conv_rate FROM driver_hourly_stats WHERE driver_id = ?",
            "created_time": 1751429485000,
            "last_updated_time": 1751429485000,
            "deleted_time": null,
            "created_by": "Fia",
            "last_updated_by": "Ludy",
            "deleted_by": null,
            "approved_by": "Endy",
            "status": "DEPLOYED",
            "description": "Conversion rate for driver"
        },
        {
            "feature_type": "batch",
            "feature_data_type": "integer",
            "query": "SELECT acc_rate FROM driver_hourly_stats WHERE driver_id = ?",
            "created_time": 1641081600000,
            "last_updated_time": 1751429485000,
            "deleted_time": null,
            "created_by": "Ludy",
            "last_updated_by": "Eka",
            "deleted_by": "Endy",
            "deleted_by": null,
            "approved_by": "Endy",
            "status": "APPROVED",
            "description": "Acceptance rate for driver"
        },
        {
            "feature_type": "real-time",
            "feature_data_type": "string",
            "query": "SELECT avg_trips FROM driver_hourly_stats WHERE driver_id = ?",
            "created_time": 1751429485000,
            "last_updated_time": 1751429485000,
            "deleted_time": 1751429485000,
            "created_by": "Eka",
            "last_updated_by": "Fia",
            "deleted_by": "Endy",
            "approved_by": "Endy",
            "status": "DELETED",
            "description": "Average daily trips"
        }
      ],
      "messages": ["200 OK", "200 OK", "200 OK"],
      "event_timestamps": [1751429485000, 1751429485000, 1751429485000] // responses timestamp
  }
}
```

## Create Feature (Single)

### Request
```json
{
  "feature": "new:feature:1",
  "feature_type": "real-time",
  "feature_data_type": "float", 
  "query": "SELECT value FROM table WHERE id = ?",
  "created_by": "developer",
  "description": "New feature description"
}
```

### Response
```json
{
    "values": {
        "feature": "new:feature:1",
        "feature_type": "real-time",
        "created_time": 1751429485000,
        "created_by": "developer",
        "status": "READY FOR TESTING",
        "description": "New feature description"
    },
    "message": "200 OK",
    "event_timestamp": 1751429485000 // responses timestamp
}
```

## Update Feature (Single)

### Request
```json
{
  "feature": "new:feature:1",
  "feature_type": "batch",
  "last_updated_by": "updater",
  "status": "TESTED",
  "description": "Updated description"
}
```

### Response
```json
{
    "values": {
        "feature": "new:feature:1",
        "feature_type": "batch",
        "last_updated_time": 1751429485000,
        "last_updated_by": "updater",
        "status": "TESTED",
        "description": "Updated description"
    },
    "message": "200 OK",
    "event_timestamp": 1751429485000 
}
```

## Delete Feature (Single)

### Request
```json
{
  "feature": "new:feature:1",
  "feature_type": "real-time",
  "deleted_by": "deleter"
}
```

### Response
```json
{
    "values": {
        "feature": "new:feature:1",
        "feature_type": "real-time",
        "deleted_time": 1751429487000,
        "status": "DELETED",
    },
  "message": "200 OK",
  "event_timestamp": 1751429487000 
}
```