# Custom Domain Mapping Guide

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
