# Webhooks Integration Guide

Webhooks allow your application to receive real-time HTTP POST notifications.

## Configuring Webhooks
1. Navigate to Settings > Webhooks in your dashboard.
2. Enter your endpoint URL (must start with `https://`).
3. Select the events you want to subscribe to (e.g., `user.created`, `payment.succeeded`).

## Signature Verification
To verify that the webhook payload was sent by Adsparkx, verify the `X-Adsparkx-Signature` header using HMAC-SHA256 and your Webhook Secret:
```python
import hmac
import hashlib

def verify_signature(payload_bytes, secret, signature):
    expected = hmac.new(secret.encode(), payload_bytes, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)
```

## Retry Policy
If your server returns a non-2xx status code, we will retry sending the webhook up to 5 times using exponential backoff over a 24-hour window.
