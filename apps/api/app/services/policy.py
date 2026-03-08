from __future__ import annotations

import re
from typing import Any

from app.config import APPROVED_KEYS

KEY_PATH_PATTERN = re.compile(r"^[A-Za-z0-9_.\-/]+$")


def is_key_allowed(key_path: str) -> bool:
    if not KEY_PATH_PATTERN.fullmatch(key_path):
        return False

    if key_path in APPROVED_KEYS:
        return True

    for allowed in APPROVED_KEYS:
        if not allowed.endswith(".*"):
            continue
        prefix = allowed[:-2]
        if key_path == prefix or key_path.startswith(prefix + "."):
            return True

    return False


def split_path(key_path: str) -> list[str]:
    return [part for part in key_path.split(".") if part]


def deep_get(data: dict[str, Any], parts: list[str]) -> Any:
    cursor: Any = data
    for part in parts:
        if not isinstance(cursor, dict) or part not in cursor:
            return None
        cursor = cursor[part]
    return cursor


def deep_set(data: dict[str, Any], parts: list[str], value: Any) -> None:
    cursor: dict[str, Any] = data
    for part in parts[:-1]:
        node = cursor.get(part)
        if not isinstance(node, dict):
            node = {}
            cursor[part] = node
        cursor = node
    cursor[parts[-1]] = value
