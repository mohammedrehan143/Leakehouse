# Policy: Security Rules & Vulnerability Governance

## 1. Secrets Management
1. **Zero Secret Commitment**: Under no circumstances may API keys, personal access tokens (PATs), database passwords, private keys, or secret tokens be hardcoded in code, commit messages, or configuration files.
2. **Environment Variable Injection**: All credentials must be read exclusively from environment variables via configuration classes.
3. **Template Preservation**: Keep `.env.example` up to date with dummy placeholder values for every required variable. Never copy production credentials into `.env.example`.

## 2. Ingestion & API Security
1. **Signature Verification**: All incoming webhooks must compute HMAC signatures over raw request bodies using the configured secret and verify with constant-time comparison.
2. **SSRF Prevention**: URL inputs must be validated against internal IP blacklists.
3. **Payload Sanitization**: Reject payloads exceeding size thresholds to defend against memory exhaustion and ReDoS attacks.

## 3. Database & SQL Protection
1. **Parameterized Queries**: Never construct SQL queries using string formatting, f-strings, or string concatenation.
2. **SQLAlchemy ORM Exclusivity**: Utilize SQLAlchemy 2.0 type-safe expressions or parameterized constructs.
3. **Least Privilege**: Application services must connect using credentials limited to required operations.

## 4. Frontend & Web Security
1. **Content Security Policy (CSP)**: Prohibit inline scripts and unsafe evals.
2. **CORS Restrictions**: Do not allow wildcard `*` origins in production environments.
3. **Sanitized Rendering**: React default escaping must be preserved. Avoid `dangerouslySetInnerHTML`.
