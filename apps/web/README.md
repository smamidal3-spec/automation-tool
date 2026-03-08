# Frontend

Next.js UI for DevOps YAML Automation Platform.

## Features
- Multi-application selection
- Runtime config fetch from backend (`/api/v1/automation/config`)
- Preview and execute integration
- Dry-run toggle for safe execution
- Diff preview and execution summary panels

## Run
```powershell
Set-Location C:\Users\mamid\vibe\apps\web
npm install
npm run dev
```

## Backend URL override
Set `NEXT_PUBLIC_API_BASE` if backend is not running at `http://localhost:8000`.
