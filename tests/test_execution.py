"""Integration test helper for the DevOps YAML Automation Platform.

This script:
1. Fetches the config endpoint to discover available applications.
2. Sends a preview request.
3. Sends an execute request.
4. Prints a human-readable summary.
"""

import sys
import httpx

BACKEND_URL = "http://127.0.0.1:8000"
HEADERS = {"Authorization": "Bearer admin-token"}


def separator(title: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


def step_discover_apps() -> list[str]:
    separator("STEP 1: Discovering applications")
    response = httpx.get(
        f"{BACKEND_URL}/api/v1/automation/config", headers=HEADERS, timeout=15.0
    )
    if response.status_code != 200:
        print(f"  FAILED: {response.status_code} - {response.text}")
        sys.exit(1)

    payload = response.json()
    apps = payload.get("applications", [])
    env_files = payload.get("environment_files", [])
    approved_keys = payload.get("approved_keys", [])

    print(f"  Found {len(apps)} applications")
    for app in apps:
        print(f"    - {app}")
    print(f"  Environment files: {env_files}")
    print(f"  Approved keys: {approved_keys}")
    return apps


def step_preview(apps: list[str]) -> None:
    separator("STEP 2: Preview replicaCount -> 5")
    targets = [{"application": app, "environment_file": "values.dev.yaml"} for app in apps]
    payload = {"key_path": "replicaCount", "new_value": 5, "targets": targets}

    response = httpx.post(
        f"{BACKEND_URL}/api/v1/automation/preview",
        headers=HEADERS,
        json=payload,
        timeout=30.0,
    )
    if response.status_code != 200:
        print(f"  FAILED: {response.status_code} - {response.text}")
        sys.exit(1)

    data = response.json()
    diffs = data.get("diffs", [])
    changed_count = sum(1 for diff in diffs if diff.get("changed"))
    error_count = sum(1 for diff in diffs if diff.get("error"))

    print(
        f"  Preview returned {len(diffs)} diffs: {changed_count} changed, {error_count} errors"
    )
    for diff in diffs[:3]:
        print(f"    [{diff['application']}] changed={diff['changed']}")
    if len(diffs) > 3:
        print(f"    ... and {len(diffs) - 3} more")


def step_execute(apps: list[str]) -> None:
    separator("STEP 3: Execute replicaCount -> 5")
    targets = [{"application": app, "environment_file": "values.dev.yaml"} for app in apps]
    payload = {
        "key_path": "replicaCount",
        "new_value": 5,
        "targets": targets,
        "confirm": True,
        "dry_run": False,
    }

    response = httpx.post(
        f"{BACKEND_URL}/api/v1/automation/execute",
        headers=HEADERS,
        json=payload,
        timeout=60.0,
    )
    if response.status_code != 200:
        print(f"  FAILED: {response.status_code} - {response.text}")
        sys.exit(1)

    data = response.json()
    results = data.get("results", [])
    success_count = sum(1 for result in results if result.get("status") == "success")
    failed_count = sum(1 for result in results if result.get("status") == "failed")

    print(
        f"\n  RESULTS: {success_count} succeeded, {failed_count} failed out of {len(results)}"
    )
    print("  " + "-" * 55)
    for result in results:
        status = "OK" if result["status"] == "success" else "FAIL"
        print(f"  {status} {result['application']}")
        print(f"      repo:   {result['repo']}")
        print(f"      branch: {result.get('branch') or '-'}")
        print(f"      PR:     {result.get('pull_request_url') or '-'}")
        if result.get("error"):
            print(f"      error:  {result['error']}")


def main() -> None:
    print("DevOps YAML Automation Platform - integration test")
    apps = step_discover_apps()
    if not apps:
        print("No applications discovered. Is the mock GitHub server running?")
        sys.exit(1)

    step_preview(apps)
    step_execute(apps)

    separator("TEST COMPLETE")
    print("Config discovery, preview, and execute paths all completed.")


if __name__ == "__main__":
    main()
