# Security

## API

- Rate limiting via `slowapi` (generate: 10/min, evaluate: 5/min, pipeline create: 5/min)
- Optional API key middleware (`NIGHTMARENET_API_KEY`)
- CORS via `NIGHTMARENET_CORS_ORIGINS` (strip whitespace in config)
- Validation on all Pydantic request bodies

## Secrets

- Never commit `.env` (listed in `.gitignore`)
- Browser Use and cloud keys only in environment variables

## Hosted Platform (planned)

- OAuth 2.0 + JWT for users
- RBAC: admin, member, viewer per organization
- Audit log on every state mutation
- Model artifacts signed with SHA-256 checksums

## Reporting

Report vulnerabilities via GitHub Security Advisories on the repository.
