# API Authentication Guide

This guide explains how to authenticate with the Adsparkx Cloud API.

## Bearer Token Authentication
All API requests must include a Bearer token in the `Authorization` header:
```http
Authorization: Bearer <YOUR_API_KEY>
```

## Token Expiration
- Developer API keys do not expire unless manually revoked.
- Session tokens expire exactly 24 hours after creation.

## Rate Limiting
- **Free Tier**: 60 requests per minute (RPM).
- **Pro Tier**: 1,000 requests per minute (RPM).
- **Enterprise Tier**: Custom limits.

If you exceed these limits, the API returns a `429 Too Many Requests` status code.

## Troubleshooting 401 Unauthorized
If you receive a `401 Unauthorized` error:
1. Verify that your API key is correct and active.
2. Check that the header format is exactly `Bearer <token>` (note the space).
3. Ensure the token has not been revoked in the Developer Console.
