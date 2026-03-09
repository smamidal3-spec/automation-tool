from app.services.policy import deep_get, deep_set, is_key_allowed, split_path


def test_key_policy_accepts_exact_and_wildcard_paths() -> None:
    assert is_key_allowed("replicaCount")
    assert is_key_allowed("ingress.annotations.nginx.ingress.kubernetes.io/rewrite-target")


def test_key_policy_rejects_unknown_or_invalid_paths() -> None:
    assert not is_key_allowed("secrets.password")
    assert not is_key_allowed("../bad")


def test_split_and_deep_helpers() -> None:
    parts = split_path("autoscaling.maxReplicas")
    assert parts == ["autoscaling", "maxReplicas"]

    payload: dict[str, object] = {}
    deep_set(payload, parts, 4)
    assert deep_get(payload, parts) == 4
