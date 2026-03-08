from __future__ import annotations

import threading
import time
from collections import defaultdict, deque

from fastapi import HTTPException, status

from app.settings import get_settings


class RateLimiter:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._requests: dict[str, deque[float]] = defaultdict(deque)

    def check(self, key: str) -> None:
        settings = get_settings()
        now = time.time()
        window_start = now - 60
        max_requests = settings.rate_limit_per_minute

        with self._lock:
            queue = self._requests[key]
            while queue and queue[0] < window_start:
                queue.popleft()

            if len(queue) >= max_requests:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded",
                )

            queue.append(now)


rate_limiter = RateLimiter()
