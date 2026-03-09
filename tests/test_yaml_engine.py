from app.services.yaml_engine import patch_yaml

BASE_YAML = """replicaCount: 2
image:
  tag: \"1.0.0\"
autoscaling:
  minReplicas: 1
  maxReplicas: 3
"""


def test_patch_yaml_updates_value_and_generates_diff() -> None:
    result = patch_yaml(BASE_YAML, "replicaCount", 5)
    assert result.changed is True
    assert result.old_value == 2
    assert "-replicaCount: 2" in result.diff
    assert "+replicaCount: 5" in result.diff


def test_patch_yaml_reports_no_change_for_same_value() -> None:
    result = patch_yaml(BASE_YAML, "replicaCount", 2)
    assert result.changed is False
    assert result.old_value == 2
