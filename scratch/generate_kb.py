import os
from pathlib import Path

# Create data directory
DATA_DIR = Path("data")
DATA_DIR.mkdir(parents=True, exist_ok=True)

# 1. Generate text and markdown files
documents = {
    "api_authentication.md": """# API Authentication Guide

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
""",

    "billing_policy.md": """# Billing and Refund Policy

This document outlines the payment terms, billing cycles, cancellation, and refund policies for Adsparkx Cloud Services.

## Subscription Billing
- Subscriptions are billed on a recurring monthly or annual basis.
- Payments are automatically processed using the payment method on file.

## Refund Policy
- We offer a **14-day money-back guarantee** for new subscriptions. Refund requests made within 14 days of the initial purchase will be fully refunded.
- No refunds will be provided after 14 days from the purchase date or for renewal charges.
- Add-on services (such as extra domain mapping or custom storage) are non-refundable.

## Account Cancellation
- Users can cancel their subscriptions at any time through the **Billing Settings** dashboard.
- Upon cancellation, your account will remain active until the end of the current billing cycle.

## Invoice Disputes
If you notice an unexpected charge or duplicate invoice:
1. Do not contact your bank first, as chargebacks delay resolution.
2. Open a support ticket immediately.
3. Provide your account email and the charge ID.
4. Our team will verify and resolve billing disputes within 2-3 business days.
""",

    "database_connection.md": """# Database Connection Guide

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
""",

    "domain_mapping.md": """# Custom Domain Mapping Guide

How to link your own domain (e.g., www.example.com) to your Adsparkx project.

## DNS Settings
Go to your DNS registrar (GoDaddy, Namecheap, Route 53) and add the following records:

### 1. Root Domain (example.com)
- **Type**: A Record
- **Host/Name**: `@`
- **Value**: `76.76.21.21`

### 2. Subdomain (www.example.com)
- **Type**: CNAME
- **Host/Name**: `www`
- **Value**: `domains.adsparkx.com`

## SSL Certificates
Once DNS records are configured, Adsparkx automatically provisions a Let's Encrypt SSL certificate for your domain within 10 to 30 minutes. Do not remove the DNS records, or the certificate renewal will fail.
""",

    "webhooks_guide.md": """# Webhooks Integration Guide

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
""",

    "gdpr_compliance.md": """# GDPR Compliance & Data Privacy

Adsparkx is committed to protecting user privacy and complying with GDPR regulations.

## Data Subject Rights
- **Right to Access**: You can download a complete export of your personal data from the Account Settings panel.
- **Right to Rectification**: Update your profile information at any time in the profile section.
- **Right to Erasure (Deletion)**: You may request permanent deletion of your account.

## Account Deletion Process
To permanently delete your account and all associated data:
1. Send an email to `privacy@adsparkx.com` with the subject "GDPR Data Erasure Request".
2. Confirm your ownership via the email confirmation link we send.
3. Your data will be permanently purged from our active databases within 7 business days and from cold backups within 30 days.
""",

    "email_delivery_issues.md": """# Troubleshooting Email Delivery Issues

If emails sent from your app are going to spam, configure your DNS authentication records.

## 1. SPF Record
Add a TXT record to authorize our mail servers:
- **Type**: TXT
- **Host**: `@`
- **Value**: `v=spf1 include:mail.adsparkx.com ~all`

## 2. DKIM Record
Configure DKIM using the public key provided in your Adsparkx Email Settings:
- **Type**: TXT
- **Host**: `adsparkx._domainkey`
- **Value**: `k=rsa; p=MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...`

## 3. DMARC Record
Add a DMARC policy:
- **Type**: TXT
- **Host**: `_dmarc`
- **Value**: `v=DMARC1; p=quarantine; pct=100; rua=mailto:dmarc-reports@yourdomain.com`
""",

    "serverless_functions.md": """# Deploying Serverless Functions

Adsparkx Serverless Functions allow you to run backend code without managing servers.

## Limitations
- **Max Execution Timeout**: 15 seconds for Free Tier, 300 seconds for Enterprise.
- **Memory Limit**: 512MB by default.
- **Language Support**: Node.js 18+, Python 3.10+, Go 1.20+.

## Environment Variables
Do not hardcode API keys or secrets in your serverless code. Instead:
1. Go to Settings > Environment Variables in the console.
2. Add your secrets.
3. Retrieve them in code using `os.environ.get("MY_SECRET")`.
""",

    "storage_cors.md": """# Configuring Storage CORS Policy

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
""",

    "team_management.md": """# Team Management and Collaboration

Adsparkx allows multiple team members to collaborate on projects.

## Member Roles and Permissions
- **Owner**: Full access, including billing, account settings, and project deletion.
- **Admin**: Can manage domains, servers, databases, and invite new members, but cannot change billing details or delete the project.
- **Developer**: Can deploy code, connect to databases, view logs, and configure environment variables.
- **Viewer**: Read-only access to the dashboard.

## Inviting Members
1. Go to Team Settings.
2. Click "Invite Member".
3. Enter the email address and select the appropriate Role.
4. The user will receive an invitation link valid for 7 days.
"""
}

# Write text/markdown files
for filename, text in documents.items():
    file_path = DATA_DIR / filename
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text.strip() + "\n")
    print(f"Created {file_path}")


# 2. Programmatically generate password_reset_guide.pdf using ReportLab
pdf_path = DATA_DIR / "password_reset_guide.pdf"

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    
    print("Generating PDF using ReportLab...")
    doc = SimpleDocTemplate(str(pdf_path), pagesize=letter,
                            rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
    
    styles = getSampleStyleSheet()
    
    # Custom Styles
    title_style = ParagraphStyle(
        'PDFTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        spaceAfter=15
    )
    
    heading_style = ParagraphStyle(
        'PDFHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        spaceBefore=10,
        spaceAfter=10
    )
    
    body_style = ParagraphStyle(
        'PDFBody',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=11,
        leading=16,
        spaceAfter=8
    )
    
    bullet_style = ParagraphStyle(
        'PDFBullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=16,
        leftIndent=20,
        firstLineIndent=-10,
        spaceAfter=6
    )

    story = []
    
    # Title
    story.append(Paragraph("Account Security & Password Reset Guide", title_style))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("This document provides detailed guidelines for password recovery, two-factor authentication configuration, and standard account security policies at Adsparkx Cloud Services.", body_style))
    story.append(Spacer(1, 10))
    
    # Section 1
    story.append(Paragraph("1. Password Reset Steps", heading_style))
    story.append(Paragraph("If you have forgotten your password or are locked out of your account, follow these exact steps to restore access:", body_style))
    story.append(Paragraph("&bull; <b>Step 1:</b> Navigate to the login portal and click the 'Forgot Password' link.", bullet_style))
    story.append(Paragraph("&bull; <b>Step 2:</b> Enter your registered email address and submit the form.", bullet_style))
    story.append(Paragraph("&bull; <b>Step 3:</b> Check your inbox for a password reset email sent from <i>no-reply@adsparkx.com</i>. (Check spam/junk folders if not received within 2 minutes).", bullet_style))
    story.append(Paragraph("&bull; <b>Step 4:</b> Click the secure reset link inside the email. The link is time-sensitive and expires exactly <b>15 minutes</b> after creation.", bullet_style))
    story.append(Paragraph("&bull; <b>Step 5:</b> Choose a new secure password that meets our corporate security requirements.", bullet_style))
    story.append(Spacer(1, 10))
    
    # Section 2
    story.append(Paragraph("2. Password Strength Requirements", heading_style))
    story.append(Paragraph("To ensure the safety of your cloud environment, your new password must comply with the following standards:", body_style))
    story.append(Paragraph("&bull; Must be at least <b>12 characters</b> in length.", bullet_style))
    story.append(Paragraph("&bull; Must contain at least one uppercase letter (A-Z).", bullet_style))
    story.append(Paragraph("&bull; Must contain at least one lowercase letter (a-z).", bullet_style))
    story.append(Paragraph("&bull; Must contain at least one numerical digit (0-9).", bullet_style))
    story.append(Paragraph("&bull; Must contain at least one special character (e.g., !, @, #, $, %, ^, &amp;, *).", bullet_style))
    story.append(Spacer(1, 10))
    
    # Section 3
    story.append(Paragraph("3. Multi-Factor Authentication (MFA)", heading_style))
    story.append(Paragraph("We strongly recommend enabling MFA to protect your account. Go to Profile Settings > Security and scan the QR code with an authenticator app (such as Google Authenticator, Microsoft Authenticator, or Authy) to link it.", body_style))
    story.append(Paragraph("If you lose your MFA device, you must enter one of the 8-digit Recovery Codes provided during MFA initialization. If you do not have your recovery codes, you must contact support to initiate identity verification.", body_style))
    
    doc.build(story)
    print(f"Successfully generated PDF: {pdf_path}")

except ImportError:
    # If reportlab is not yet installed in the current python context (e.g. while installing in venv),
    # we'll print a warning. The pip install will eventually install it and we can rerun this file.
    print("ReportLab not installed. The PDF will be generated later when running the setup script.")
