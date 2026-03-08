from __future__ import annotations

import base64
from dataclasses import dataclass
from typing import Any

import httpx

from app.services.retry import run_with_retry
from app.settings import get_settings


@dataclass
class GitFile:
    content: str
    sha: str | None = None


@dataclass
class RepoRecord:
    name: str
    full_name: str
    default_branch: str


class GitProvider:
    def list_repositories(self, org: str) -> list[RepoRecord]:
        raise NotImplementedError

    def fetch_file(self, repo: str, file_path: str, ref: str, dry_run: bool | None = None) -> GitFile:
        raise NotImplementedError

    def create_branch(self, repo: str, source_branch: str, new_branch: str, dry_run: bool | None = None) -> None:
        raise NotImplementedError

    def commit_file(
        self,
        repo: str,
        branch: str,
        file_path: str,
        content: str,
        message: str,
        dry_run: bool | None = None,
    ) -> None:
        raise NotImplementedError

    def create_pull_request(
        self,
        repo: str,
        branch: str,
        base: str,
        title: str,
        body: str,
        reviewers: list[str] | None = None,
        dry_run: bool | None = None,
    ) -> str:
        raise NotImplementedError


class GitHubProvider(GitProvider):
    def __init__(self) -> None:
        self.settings = get_settings()

    def _headers(self) -> dict[str, str]:
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.settings.github_token:
            headers["Authorization"] = f"Bearer {self.settings.github_token}"
        return headers

    def _request(self, method: str, path: str, *, params: dict[str, Any] | None = None, json: dict[str, Any] | None = None) -> httpx.Response:
        url = f"{self.settings.github_api_url.rstrip('/')}{path}"

        def _call() -> httpx.Response:
            with httpx.Client(timeout=25.0) as client:
                response = client.request(method, url, headers=self._headers(), params=params, json=json)
                return response

        return run_with_retry(_call)

    def _is_dry_run(self, dry_run: bool | None) -> bool:
        return self.settings.dry_run_default if dry_run is None else dry_run

    def list_repositories(self, org: str) -> list[RepoRecord]:
        if not self.settings.github_token:
            return []

        records: list[RepoRecord] = []
        page = 1
        while True:
            response = self._request(
                "GET",
                f"/orgs/{org}/repos",
                params={"type": "all", "sort": "full_name", "per_page": 100, "page": page},
            )
            if response.status_code == 404:
                response = self._request(
                    "GET",
                    f"/users/{org}/repos",
                    params={"type": "all", "sort": "full_name", "per_page": 100, "page": page},
                )
            if response.status_code >= 400:
                raise ValueError(f"Repository list failed for {org}: {response.status_code} {response.text}")

            payload = response.json()
            if not payload:
                break

            for item in payload:
                full_name = item.get("full_name")
                repo_name = item.get("name")
                default_branch = item.get("default_branch") or "main"
                if not full_name or not repo_name:
                    continue
                records.append(
                    RepoRecord(
                        name=repo_name,
                        full_name=full_name,
                        default_branch=default_branch,
                    )
                )

            page += 1

        return records

    def fetch_file(self, repo: str, file_path: str, ref: str, dry_run: bool | None = None) -> GitFile:
        if self._is_dry_run(dry_run) or not self.settings.github_token:
            return GitFile(
                content=(
                    "replicaCount: 2\n"
                    "image:\n"
                    "  tag: \"1.0.0\"\n"
                    "autoscaling:\n"
                    "  minReplicas: 1\n"
                    "  maxReplicas: 3\n"
                    "ingress:\n"
                    "  annotations:\n"
                    "    nginx.ingress.kubernetes.io/rewrite-target: /\n"
                ),
                sha="dry-run-sha",
            )

        response = self._request("GET", f"/repos/{repo}/contents/{file_path}", params={"ref": ref})
        if response.status_code >= 400:
            raise ValueError(f"GitHub fetch failed for {repo}/{file_path}: {response.status_code} {response.text}")

        payload = response.json()
        if payload.get("encoding") != "base64":
            raise ValueError("Unsupported GitHub file encoding")

        encoded = payload.get("content", "").replace("\n", "")
        decoded = base64.b64decode(encoded).decode("utf-8")
        return GitFile(content=decoded, sha=payload.get("sha"))

    def create_branch(self, repo: str, source_branch: str, new_branch: str, dry_run: bool | None = None) -> None:
        if self._is_dry_run(dry_run) or not self.settings.github_token:
            return

        source = self._request("GET", f"/repos/{repo}/git/ref/heads/{source_branch}")
        if source.status_code >= 400:
            raise ValueError(f"Source branch lookup failed: {source.status_code} {source.text}")

        source_sha = source.json().get("object", {}).get("sha")
        if not source_sha:
            raise ValueError("Missing source SHA for branch creation")

        branch = self._request(
            "POST",
            f"/repos/{repo}/git/refs",
            json={"ref": f"refs/heads/{new_branch}", "sha": source_sha},
        )
        if branch.status_code in (200, 201):
            return
        if branch.status_code == 422:
            return
        raise ValueError(f"Branch creation failed: {branch.status_code} {branch.text}")

    def commit_file(
        self,
        repo: str,
        branch: str,
        file_path: str,
        content: str,
        message: str,
        dry_run: bool | None = None,
    ) -> None:
        if self._is_dry_run(dry_run) or not self.settings.github_token:
            return

        file_info = self.fetch_file(repo, file_path, branch, dry_run=dry_run)
        encoded_content = base64.b64encode(content.encode("utf-8")).decode("ascii")
        payload: dict[str, Any] = {
            "message": message,
            "content": encoded_content,
            "branch": branch,
        }
        if file_info.sha:
            payload["sha"] = file_info.sha

        response = self._request("PUT", f"/repos/{repo}/contents/{file_path}", json=payload)
        if response.status_code >= 400:
            raise ValueError(f"Commit failed: {response.status_code} {response.text}")

    def create_pull_request(
        self,
        repo: str,
        branch: str,
        base: str,
        title: str,
        body: str,
        reviewers: list[str] | None = None,
        dry_run: bool | None = None,
    ) -> str:
        if self._is_dry_run(dry_run) or not self.settings.github_token:
            return f"https://github.com/{repo}/pull/dry-run-{branch.replace('/', '-')[:32]}"

        pr_response = self._request(
            "POST",
            f"/repos/{repo}/pulls",
            json={"title": title, "body": body, "head": branch, "base": base},
        )
        if pr_response.status_code >= 400:
            raise ValueError(f"PR creation failed: {pr_response.status_code} {pr_response.text}")

        pr_payload = pr_response.json()
        pr_number = pr_payload.get("number")
        pr_url = pr_payload.get("html_url")

        if reviewers and pr_number:
            reviewer_response = self._request(
                "POST",
                f"/repos/{repo}/pulls/{pr_number}/requested_reviewers",
                json={"reviewers": reviewers},
            )
            if reviewer_response.status_code >= 400:
                raise ValueError(
                    f"PR reviewers assignment failed: {reviewer_response.status_code} {reviewer_response.text}"
                )

        if not pr_url:
            raise ValueError("Missing pull request URL")
        return pr_url


def get_git_provider() -> GitProvider:
    return GitHubProvider()
