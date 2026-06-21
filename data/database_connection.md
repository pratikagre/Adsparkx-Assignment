# Database Connection Guide

This guide describes how to connect to databases hosted on Adsparkx.

## PostgreSQL Connection
To connect to your hosted PostgreSQL database, use the following connection format:
```
postgresql://<username>:<password>@postgres.adsparkx.com:5432/<db_name>?sslmode=require
```

## MongoDB Connection
To connect to your MongoDB replica set:
```
mongodb+srv://<username>:<password>@mongo.adsparkx.com/<db_name>?retryWrites=true&w=majority
```

## Security Requirements
- **SSL**: SSL is strictly required (`sslmode=require` or `tls=true`). Connections without SSL will be rejected.
- **Firewall**: You must whitelist the client IP address in the Database Security panel before connecting.
