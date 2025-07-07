# API Payload Examples

## Read/Retrieve Features (Multiple)

### Request
```json
{
  "features": [
    "driver_hourly_stats:conv_rate:1", 
    "driver_hourly_stats:acc_rate:2", 
    "driver_hourly_stats:avg_daily_trips:3"
  ],
  "event_timestamp": 1751429485000
}
```

### Response
```json
{
  "metadata": {
    "feature_names": [
      "driver_hourly_stats:conv_rate:1",
      "driver_hourly_stats:acc_rate:2", 
      "driver_hourly_stats:avg_daily_trips:3"
    ]
  },
  "results": [
    {
      "values": [
        {
          "feature_type": "real-time",
          "feature_data_type": "float",
          "query": "SELECT conv_rate FROM driver_hourly_stats WHERE driver_id = ?",
          "created_time": 1751429485000,
          "updated_time": 1751429485000,
          "created_by": "Fia",
          "last_updated_by": "Ludy",
          "approved_by": "Endy",
          "status": "DEPLOYED",
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
        },
        {
          "feature_type": "real-time",
          "feature_data_type": "string",
          "query": "SELECT avg_trips FROM driver_hourly_stats WHERE driver_id = ?",
          "created_time": 1751429485000,
          "updated_time": 1751429485000,
          "created_by": "Eka",
          "last_updated_by": "Fia",
          "approved_by": null,
          "status": null,
          "description": "Average daily trips"
        }
      ],
      "statuses": ["200 OK", "200 OK", "200 OK"],
      "event_timestamps": [1751429485000, 1751429485000, 1751429485000]
    }
  ]
}
```

## Create Feature (Single)

### Request
```json
{
  "feature_name": "new:feature:1",
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
  "message": "Feature created successfully",
  "feature_name": "new:feature:1",
  "created_time": 1751429485000
}
```

## Update Feature (Single)

### Request
```json
{
  "feature_type": "batch",
  "last_updated_by": "updater",
  "status": "TESTED",
  "description": "Updated description"
}
```

### Response
```json
{
  "message": "Feature updated successfully", 
  "feature_name": "new:feature:1",
  "updated_time": 1751429486000
}
```

## Delete Feature (Single)

### Request
```
DELETE /features/new:feature:1
```

### Response
```json
{
  "message": "Feature deleted successfully",
  "feature_name": "new:feature:1", 
  "deleted_time": 1751429487000
}
```