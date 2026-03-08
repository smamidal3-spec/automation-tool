from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "development"
    database_url: str = "sqlite:///./automation.db"

    auth_mode: str = "dev"
    jwt_secret: str | None = None
    jwt_algorithm: str = "HS256"
    static_tokens: str = "admin-token:admin,editor-token:editor,viewer-token:viewer"

    rate_limit_per_minute: int = 120

    github_api_url: str = "https://api.github.com"
    github_token: str | None = None
    github_orgs: str = ""
    managed_repos: str = ""
    repo_refresh_seconds: int = 300
    dry_run_default: bool = True
    branch_prefix: str = "automation"
    commit_message_template: str = "chore(automation): update {key_path} in {environment_file}"
    required_reviewers: str = ""

    allowed_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    @staticmethod
    def _parse_csv(raw: str) -> list[str]:
        return [item.strip() for item in raw.split(",") if item.strip()]

    def parse_allowed_origins(self) -> list[str]:
        return self._parse_csv(self.allowed_origins)

    def parse_required_reviewers(self) -> list[str]:
        return self._parse_csv(self.required_reviewers)

    def parse_github_orgs(self) -> list[str]:
        return self._parse_csv(self.github_orgs)

    def parse_managed_repos(self) -> list[str]:
        return self._parse_csv(self.managed_repos)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
