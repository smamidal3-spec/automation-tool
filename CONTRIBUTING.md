# Contributing

## Local Setup
1. Install backend dependencies: `pip install -r apps/api/requirements.txt`
2. Install frontend dependencies: `cd apps/web && npm install`
3. Start services or use Docker Compose.

## Code Standards
- Keep business logic inside `app/services` modules.
- Add unit tests for every policy or YAML behavior change.
- Preserve backwards compatibility for public API contracts.
- Update docs/examples whenever request/response shape changes.

## Pull Request Checklist
- [ ] Unit tests added/updated
- [ ] API examples updated
- [ ] No secrets committed
- [ ] README/docs updated if needed
