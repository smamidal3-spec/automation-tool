from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class UpdateTarget(BaseModel):
    application: str
    environment_file: str = Field(pattern=r"^values\..+\.ya?ml$")


class PreviewRequest(BaseModel):
    key_path: str
    new_value: Any
    targets: list[UpdateTarget]


class DiffItem(BaseModel):
    application: str
    environment_file: str
    repo: str
    changed: bool
    diff: str
    updated_yaml: str | None = None
    error: str | None = None


class PreviewResponse(BaseModel):
    allowed: bool
    diffs: list[DiffItem]


class ExecuteRequest(PreviewRequest):
    confirm: Literal[True]
    dry_run: bool | None = None


class ExecuteResult(BaseModel):
    application: str
    repo: str
    branch: str | None = None
    pull_request_url: str | None = None
    status: Literal["success", "failed"]
    error: str | None = None


class ExecuteResponse(BaseModel):
    results: list[ExecuteResult]


class AuditEvent(BaseModel):
    user_id: str
    role: str
    timestamp: datetime
    repo: str
    file_path: str
    key_path: str
    old_value: Any
    new_value: Any
    pull_request_url: str | None = None
    status: Literal["success", "failed"]
    error: str | None = None


class AuditLogItem(BaseModel):
    id: int
    user_id: str
    role: str
    timestamp: datetime
    repo: str
    file_path: str
    key_path: str
    old_value: Any
    new_value: Any
    pull_request_url: str | None
    status: str
    error: str | None


class ConfigResponse(BaseModel):
    approved_keys: list[str]
    applications: list[str]
    environment_files: list[str]
