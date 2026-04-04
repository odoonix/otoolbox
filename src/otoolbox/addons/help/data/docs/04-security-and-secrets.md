# Security & Secret Handling

## Secrets
- Do not hardcode secrets in source files, tests, or examples.
- Use environment variables or Odoo configuration for credentials.
- Avoid logging sensitive values (tokens, shared secrets, passwords).

## Integrations
- For connector/API work, keep payload examples sanitized.
- Ensure error messages are useful without exposing credentials.

## Review Checklist
- No credentials in git diff.
- No plaintext secrets in XML/CSV data files.
- No accidental secret exposure in chatter/log messages.
