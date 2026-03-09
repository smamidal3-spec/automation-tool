# Architecture

## High-Level Components
- `apps/api/app/main.py`: FastAPI app and middleware
- `apps/api/app/routers/automation.py`: endpoint orchestration
- `apps/api/app/services/`: policy, YAML patching, Git provider, rate limiting, audit
- `apps/web`: Next.js interface
- `tests`: integration and unit tests

## Request Lifecycle
1. Operator submits key-path update targets
2. Policy layer validates key-path allow-list
3. YAML engine creates deterministic diffs
4. Execute flow creates branch, commits file, and opens PR
5. Audit service stores operation outcome

## Safety Controls
- Key path regex validation + allow-list wildcard support
- Dry-run mode defaults to safe no-op side effects
- Role and rate limit checks per endpoint

See [../assets/architecture.svg](../assets/architecture.svg).
