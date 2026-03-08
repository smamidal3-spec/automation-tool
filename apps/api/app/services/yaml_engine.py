from __future__ import annotations

import difflib
from dataclasses import dataclass
from io import StringIO
from typing import Any

from ruamel.yaml import YAML

from app.services.policy import deep_get, deep_set, split_path


yaml_parser = YAML()
yaml_parser.preserve_quotes = True
yaml_parser.indent(mapping=2, sequence=4, offset=2)


@dataclass
class YamlPatchResult:
    changed: bool
    old_value: Any
    updated_yaml: str
    diff: str


def patch_yaml(yaml_text: str, key_path: str, new_value: Any) -> YamlPatchResult:
    parsed = yaml_parser.load(yaml_text) or {}
    if not isinstance(parsed, dict):
        raise ValueError("YAML root must be a mapping")

    parts = split_path(key_path)
    old_value = deep_get(parsed, parts)
    deep_set(parsed, parts, new_value)

    out = StringIO()
    yaml_parser.dump(parsed, out)
    updated_yaml = out.getvalue()

    changed = old_value != new_value
    diff = "".join(
        difflib.unified_diff(
            yaml_text.splitlines(keepends=True),
            updated_yaml.splitlines(keepends=True),
            fromfile="before.yaml",
            tofile="after.yaml",
        )
    )

    return YamlPatchResult(changed=changed, old_value=old_value, updated_yaml=updated_yaml, diff=diff)
