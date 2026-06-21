# Configuring Storage CORS Policy

Cross-Origin Resource Sharing (CORS) permits web clients to access resources in your storage buckets.

## JSON CORS Configuration
Create a JSON file named `cors_config.json`:
```json
[
  {
    "origin": ["*"],
    "method": ["GET", "PUT", "POST", "DELETE", "HEAD"],
    "responseHeader": ["Content-Type", "Authorization"],
    "maxAgeSeconds": 3600
  }
]
```

## Applying CORS
Apply this configuration using the CLI:
```bash
adsparkx storage cors set gs://your-bucket-name cors_config.json
```
