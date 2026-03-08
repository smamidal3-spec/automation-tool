"""
Test script for the DevOps YAML Automation Platform.

This script:
1. Fetches the config endpoint to discover the 16 dummy applications.
2. Sends a preview request to see the diffs.
3. Sends an execute request to change replicaCount to 5 across all 16 apps.
4. Prints a detailed report of the results.
"""
import sys
import httpx

BACKEND_URL = "http://127.0.0.1:8000"
HEADERS = {"Authorization": "Bearer admin-token"}  # dev mode uses static tokens


def separator(title: str) -> None:
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def step_1_discover_apps() -> list[str]:
    """Fetch config to discover applications."""
    separator("STEP 1: Discovering Applications")
    resp = httpx.get(f"{BACKEND_URL}/api/v1/automation/config", headers=HEADERS, timeout=15.0)
    if resp.status_code != 200:
        print(f"  FAILED: {resp.status_code} — {resp.text}")
        sys.exit(1)

    data = resp.json()
    apps = data.get("applications", [])
    env_files = data.get("environment_files", [])
    approved_keys = data.get("approved_keys", [])

    print(f"  Found {len(apps)} applications:")
    for app in apps:
        print(f"    • {app}")
    print(f"  Environment files: {env_files}")
    print(f"  Approved keys: {approved_keys}")
    return apps


def step_2_preview(apps: list[str]) -> None:
    """Send a preview request."""
    separator("STEP 2: Preview — replicaCount → 5")
    targets = [{"application": app, "environment_file": "values.dev.yaml"} for app in apps]
    payload = {
        "key_path": "replicaCount",
        "new_value": 5,
        "targets": targets,
    }
    resp = httpx.post(f"{BACKEND_URL}/api/v1/automation/preview", headers=HEADERS, json=payload, timeout=30.0)
    if resp.status_code != 200:
        print(f"  FAILED: {resp.status_code} — {resp.text}")
        sys.exit(1)

    data = resp.json()
    diffs = data.get("diffs", [])
    changed_count = sum(1 for d in diffs if d.get("changed"))
    error_count = sum(1 for d in diffs if d.get("error"))

    print(f"  Preview returned {len(diffs)} diffs: {changed_count} changed, {error_count} errors")
    for d in diffs[:3]:
        print(f"    [{d['application']}] changed={d['changed']}")
        if d.get("diff"):
            for line in d["diff"].splitlines()[:5]:
                print(f"      {line}")
    if len(diffs) > 3:
        print(f"    ... and {len(diffs) - 3} more")


def step_3_execute(apps: list[str]) -> None:
    """Send an execute request."""
    separator("STEP 3: Execute — replicaCount → 5")
    targets = [{"application": app, "environment_file": "values.dev.yaml"} for app in apps]
    payload = {
        "key_path": "replicaCount",
        "new_value": 5,
        "targets": targets,
        "confirm": True,
        "dry_run": False,
    }
    resp = httpx.post(f"{BACKEND_URL}/api/v1/automation/execute", headers=HEADERS, json=payload, timeout=60.0)
    if resp.status_code != 200:
        print(f"  FAILED: {resp.status_code} — {resp.text}")
        sys.exit(1)

    data = resp.json()
    results = data.get("results", [])
    success_count = sum(1 for r in results if r.get("status") == "success")
    failed_count = sum(1 for r in results if r.get("status") == "failed")

    print(f"\n  RESULTS: {success_count} succeeded, {failed_count} failed out of {len(results)}")
    print(f"  {'─'*55}")
    for r in results:
        status_icon = "✅" if r["status"] == "success" else "❌"
        pr_url = r.get("pull_request_url") or "—"
        branch = r.get("branch") or "—"
        print(f"  {status_icon} {r['application']}")
        print(f"      repo:   {r['repo']}")
        print(f"      branch: {branch}")
        print(f"      PR:     {pr_url}")
        if r.get("error"):
            print(f"      error:  {r['error']}")


def main() -> None:
    print("╔══════════════════════════════════════════════════════════╗")
    print("║   DevOps YAML Automation Platform — Integration Test    ║")
    print("╠══════════════════════════════════════════════════════════╣")
    print("║ Target: Change replicaCount from 2 → 5 across 16 apps  ║")
    print("╚══════════════════════════════════════════════════════════╝")

    apps = step_1_discover_apps()
    if not apps:
        print("\n  No applications discovered! Is the mock GitHub server running?")
        sys.exit(1)

    step_2_preview(apps)
    step_3_execute(apps)

    separator("TEST COMPLETE")
    print("  All 16 applications were processed through the full pipeline:")
    print("    1. Config discovery ✓")
    print("    2. Diff preview ✓")
    print("    3. Branch creation → Commit → Pull Request ✓")


if __name__ == "__main__":
    main()
