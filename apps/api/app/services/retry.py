from __future__ import annotations

import time
from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")


def run_with_retry(func: Callable[[], T], retries: int = 3, base_delay: float = 0.4) -> T:
    last_exc: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            return func()
        except Exception as exc:  # pragma: no cover - generic retry wrapper
            last_exc = exc
            if attempt == retries:
                break
            time.sleep(base_delay * attempt)
    assert last_exc is not None
    raise last_exc
