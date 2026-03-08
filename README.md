# DevOps YAML Automation Platform

Production baseline implementation derived from `DevOps_YAML_Automation_PRD_Final_Production.pdf`.

## What is implemented
- Multi-application YAML updates with strict key allow-list checks.
- Structural YAML parsing and patching (preserves formatting style with `ruamel.yaml`).
- Diff preview before execution.
- Parallel per-repository processing for preview and execute.
- GitHub workflow automation service:
  - fetch file from repository
  - create branch
  - commit updated YAML
  - open pull request
  - assign reviewers (optional)
- Safe `dry_run` mode (default true) for no-op PR simulation.
- RBAC-enabled API authentication foundation (`admin`, `editor`, `viewer`).
- Rate limiting per user.
- Persistent audit logs in database (default SQLite, configurable for PostgreSQL).
- Config endpoint for frontend runtime data (`approved keys`, apps, env files).

## Project structure
- `apps/api`: FastAPI backend
- `apps/web`: Next.js frontend

## Local run (without Docker)
### Backend
```powershell
Set-Location C:\Users\mamid\vibe\apps\api
Copy-Item .env.example .env -Force
py -3.11 -m venv venv311
.\venv311\Scripts\python.exe -m pip install --upgrade pip
.\venv311\Scripts\python.exe -m pip install -r requirements.txt
.\venv311\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

### Frontend
```powershell
Set-Location C:\Users\mamid\vibe\apps\web
npm install
npm run dev
```

## Deploy for other users (Docker)
This is the quickest way to host the tool so others can open it from their machines.

### 1) Prepare environment
```powershell
Set-Location C:\Users\mamid\vibe
Copy-Item .env.deploy.example .env -Force
notepad .env
```

Set at least:
- `GITHUB_TOKEN=<token with repo contents + pull request write access>`
- `GITHUB_ORGS=<org1,org2>` and/or `MANAGED_REPOS=<org/repo-a,org/repo-b>`
- `DRY_RUN_DEFAULT=false` for real branch/commit/PR execution.
- `NEXT_PUBLIC_API_BASE` to your public backend URL if needed.
- `ALLOWED_ORIGINS` to your public frontend URL.

### 2) Start stack
```powershell
docker compose up -d --build
```

### 3) Open URLs
- Frontend: `http://localhost:3000`
- Backend health: `http://localhost:8000/health`

### 4) Make it accessible to others
- Host this on a cloud VM/container platform.
- Attach a domain (for example `yaml-automation.yourcompany.com`).
- Expose ports 80/443 through reverse proxy (Nginx/Caddy/Traefik).
- Share only the frontend URL with users.

## API endpoints
- `GET /health`
- `GET /api/v1/automation/config`
- `POST /api/v1/automation/preview`
- `POST /api/v1/automation/execute`
- `GET /api/v1/automation/audit` (admin only)

## Auth
- `AUTH_MODE=dev`: no manual user/token input in UI; backend treats requests as system user.
- `AUTH_MODE=token`: backend supports bearer-token RBAC, but UI login flow must be added before enabling it.

## Important production notes
- Repository names are discovered from `GITHUB_ORGS` or explicitly controlled with `MANAGED_REPOS`.
- Set `DRY_RUN_DEFAULT=false` only after verifying preview results.
- Keep `GITHUB_TOKEN` in server secrets, never in frontend code.
