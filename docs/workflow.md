# Workflow

## Development
1. Run mock GitHub server from `tests/mock_github.py`
2. Start API and frontend
3. Execute preview and execute requests from `examples/`
4. Confirm audit log entries

## Release
1. Run tests
2. Build web app and backend image
3. Deploy using Docker Compose/target platform
4. Verify `/health` and automation endpoints
