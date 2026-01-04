# Security Policy

## Supported Versions

Use this section to tell people about which versions of your project are currently being supported with security updates.

| Version | Supported          |
| ------- | ------------------ |
| v1.0.x  | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take the security of our software very seriously. If you have found a security vulnerability, we appreciate your help in disclosing it to us in a responsible manner.

### How to report

Please do not report security vulnerabilities through public GitHub issues.

Instead, please report them via email to: **security@andyanh.id.vn** (or contact the maintainer directly).

### What to include

Please include the following details in your report:

- A description of the vulnerability.
- Steps to reproduce the issue.
- Potential impact of the vulnerability.

### Response timeline

We will acknowledge receipt of your report within 48 hours. We will perform a preliminary assessment and stay in touch with you about the progress of the resolution.

## Security Best Practices Implemented

This project follows several security best practices:
- **Environment Variables**: Sensitive data (Database credentials, API keys) are managed via `.env` files and GitHub Secrets.
- **Docker Isolation**: Services (DB, Redis, App) run in isolated containers.
- **HTTPS/SSL**: The application is configured to run behind secure domains (`CSRF_TRUSTED_ORIGINS`).
- **Access Control**: Built-in access code authentication middleware.
