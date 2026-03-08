from __future__ import annotations

from dataclasses import dataclass
from time import monotonic
from typing import Any

from app.config import ENV_FILES
from app.services.git_provider import GitProvider, get_git_provider
from app.settings import get_settings


@dataclass
class RepoDetails:
    repo: str
    default_branch: str
    files: list[str]


class RepositoryRegistry:
    def __init__(self, provider: GitProvider) -> None:
        self._provider = provider
        self._settings = get_settings()
        self._last_refresh = 0.0
        self._repo_map: dict[str, RepoDetails] = {}

    def _from_managed_repos(self) -> dict[str, RepoDetails]:
        mapping: dict[str, RepoDetails] = {}
        for full_name in self._settings.parse_managed_repos():
            app_name = full_name.split("/")[-1]
            mapping[app_name] = RepoDetails(
                repo=full_name,
                default_branch="main",
                files=list(ENV_FILES.values()),
            )
        return mapping

    def _from_github_orgs(self) -> dict[str, RepoDetails]:
        mapping: dict[str, RepoDetails] = {}
        for org in self._settings.parse_github_orgs():
            try:
                records = self._provider.list_repositories(org)
            except Exception:
                continue
            for record in records:
                mapping[record.name] = RepoDetails(
                    repo=record.full_name,
                    default_branch=record.default_branch,
                    files=list(ENV_FILES.values()),
                )
        return mapping

    def refresh(self, force: bool = False) -> None:
        ttl = max(self._settings.repo_refresh_seconds, 30)
        if not force and self._repo_map and (monotonic() - self._last_refresh) < ttl:
            return

        mapping = self._from_managed_repos()
        github_mapping = self._from_github_orgs()
        mapping.update(github_mapping)

        self._repo_map = mapping
        self._last_refresh = monotonic()

    def applications(self) -> list[str]:
        self.refresh()
        return sorted(self._repo_map.keys())

    def get_repo_details(self, application: str) -> dict[str, Any]:
        self.refresh()
        details = self._repo_map.get(application)
        if not details:
            raise ValueError(
                f"Unknown application: {application}. Configure MANAGED_REPOS or GITHUB_ORGS in backend settings."
            )
        return {
            "repo": details.repo,
            "default_branch": details.default_branch,
            "files": details.files,
        }


repo_registry = RepositoryRegistry(get_git_provider())
