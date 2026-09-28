"""FastAPI middleware for Request-ID propagation and rate limiting."""

from __future__ import annotations

import time
import uuid
from collections import defaultdict
from collections.abc import Callable
from typing import Any

from fastapi import HTTPException, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class RequestIdMiddleware(BaseHTTPMiddleware):
    """Middleware that ensures every request has a unique X-Request-ID header."""

    async def dispatch(self, request: Request, call_next: Callable[[Request], Any]) -> Response:
        req_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = req_id

        response: Response = await call_next(request)
        response.headers["X-Request-ID"] = req_id
        return response


class InMemoryRateLimiter:
    """Sliding-window rate limiter per client IP."""

    def __init__(self, requests_per_minute: int = 60) -> None:
        self.requests_per_minute = requests_per_minute
        self._history: dict[str, list[float]] = defaultdict(list)

    def check(self, client_ip: str) -> bool:
        """Check if request from client_ip is within the allowed rate limit."""
        now = time.time()
        window_start = now - 60.0
        # Clean expired timestamps
        active = [t for t in self._history[client_ip] if t > window_start]
        if len(active) >= self.requests_per_minute:
            self._history[client_ip] = active
            return False

        active.append(now)
        self._history[client_ip] = active
        return True

    def reset(self) -> None:
        """Clear all rate limiting records."""
        self._history.clear()


# Default global rate limiter instance (configured from settings)
default_rate_limiter = InMemoryRateLimiter(requests_per_minute=60)


async def check_rate_limit(request: Request) -> None:
    """Dependency for public routes enforcing rate limits (PRD §7)."""
    # Use client IP or fallback header
    client_ip = request.client.host if request.client else "unknown"
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        client_ip = forwarded.split(",")[0].strip()

    if not default_rate_limiter.check(client_ip):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please try again later.",
            headers={"Retry-After": "60"},
        )
