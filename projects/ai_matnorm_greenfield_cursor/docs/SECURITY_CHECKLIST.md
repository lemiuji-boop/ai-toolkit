# Security Checklist

## Access

- [ ] HTTPS in production.
- [ ] VPN recommended for first deployment.
- [x] JWT access + refresh tokens.
- [x] RBAC on every protected endpoint.
- [x] Admin routes protected by admin role.
- [x] Rate limits on login and upload.

## Files

- [ ] MIME validation.
- [ ] File size limits.
- [ ] Quarantine before processing.
- [ ] No direct execution of uploaded files.
- [ ] Safe archive extraction.
- [ ] Path traversal protection.
- [ ] Zip slip protection.

## Secrets

- [x] API keys server-side only.
- [x] Encryption at rest for secrets.
- [ ] Secrets masked in logs.
- [ ] Per-provider usage limits.

## AI Safety

- [ ] Prompt injection detection.
- [ ] External provider policy: which documents may be sent outside local server.
- [ ] PII/secret redaction where needed.
- [x] JSON schema validation for all AI outputs.
- [ ] No direct execution of AI-generated code.

## Audit

- [ ] User actions logged.
- [ ] Admin actions logged.
- [ ] Data export logged.
- [ ] Failed auth attempts logged.
- [ ] Provider failures logged.
