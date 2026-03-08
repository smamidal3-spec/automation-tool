from __future__ import annotations

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

APPROVED_KEYS = {
    "replicaCount",
    "autoscaling.minReplicas",
    "autoscaling.maxReplicas",
    "image.tag",
    "ingress.annotations.*",
}

ENV_FILES = {
    "dev": "values.dev.yaml",
    "qa.east1": "values.qa.east1.yaml",
    "qa.west1": "values.qa.west1.yaml",
    "stage": "values.stage.yaml",
    "prod": "values.prod.yaml",
}


def approved_keys() -> list[str]:
    return sorted(APPROVED_KEYS)
