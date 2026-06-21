# Troubleshooting Email Delivery Issues

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
