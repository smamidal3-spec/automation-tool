# DevOps YAML Automation Platform

## Project Title
DevOps YAML Automation Platform

## Project Overview
A full-stack automation platform that safely applies controlled YAML updates across multiple repositories and opens pull requests through GitHub APIs.

## Motivation
Teams often apply repetitive configuration updates (for example `replicaCount`, image tags, and autoscaling settings) across many service repositories. This project reduces manual mistakes by centralizing allowed-change policy, diff preview, and audited execution.

## Features
- FastAPI backend with preview and execute endpoints
- YAML patch engine preserving formatting via `ruamel.yaml`
- Key-path allow-list policy enforcement
- Repository discovery and GitHub PR automation
- Role-based access controls and rate limiting
- Audit log persistence (SQLite/PostgreSQL)
- Next.js frontend for operator workflows

## Tech Stack
- Python, FastAPI, SQLAlchemy, Pydantic
- ruamel.yaml, httpx
- Next.js + TypeScript
- Docker Compose

## Architecture Explanation
- `apps/api`: orchestration API and service layer
- `apps/web`: operator dashboard UI
- `tests`: integration helper and unit tests
- `examples`: sample request/response payloads

Detailed diagrams and flow docs are in [docs/architecture.md](docs/architecture.md).

## Installation Instructions
### Backend
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r apps/api/requirements.txt
uvicorn app.main:app --app-dir apps/api --reload --port 8000
```

### Frontend
```bash
cd apps/web
npm install
npm run dev
```

### Docker
```bash
docker compose up -d --build
```

## Usage Example
Preview a change before executing:
```bash
curl -X POST http://127.0.0.1:8000/api/v1/automation/preview \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer admin-token" \
  -d @examples/preview-request.json
```

## Example Output
See [examples/preview-response.json](examples/preview-response.json) and [examples/execute-response.json](examples/execute-response.json).

## Testing
```bash
pytest tests/test_policy.py tests/test_yaml_engine.py -q
```

## Future Improvements
- GitHub App auth flow instead of static token auth
- Bulk rollback operation for multi-repo updates
- Webhook-driven completion updates in UI
- CI pipeline with contract tests for provider adapters
