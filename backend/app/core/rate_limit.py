"""
Lightweight in-memory per-user rate limiting for the expensive LLM endpoints.

A troll hammering the chat endpoint (e.g. 100 requests/second) would otherwise
burn the Groq API budget and slow the app for everyone. This caps how many
requests a single user can make in a rolling time window and returns HTTP 429
once the cap is hit.

Note: state is per-process and in-memory. That is exactly right for the local
uvicorn backend (single process). On Vercel serverless each warm instance keeps
its own counter — still useful against a burst, but a distributed store (Redis /
Upstash) would be needed for hard cross-instance limits in production.
"""
import time
from collections import defaultdict, deque
from typing import Deque, Dict

from fastapi import Depends, HTTPException, status

from app.core.security import get_current_user
from app.domain.models import Profile


class SlidingWindowRateLimiter:
    """Allow at most `max_requests` per `window_seconds` for a given key."""

    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._hits: Dict[str, Deque[float]] = defaultdict(deque)

    def check(self, key: str) -> None:
        now = time.time()
        cutoff = now - self.window_seconds
        hits = self._hits[key]

        # Drop timestamps that fell out of the rolling window.
        while hits and hits[0] < cutoff:
            hits.popleft()

        if len(hits) >= self.max_requests:
            retry_after = int(hits[0] + self.window_seconds - now) + 1
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=(
                    f"Rate limit exceeded — max {self.max_requests} requests per "
                    f"{self.window_seconds}s. Please wait {retry_after}s and try again."
                ),
                headers={"Retry-After": str(retry_after)},
            )

        hits.append(now)


# Chat queries each trigger up to two Groq calls (SQL + explanation), so this cap
# comfortably covers real analytical use while stopping abusive request floods.
CHAT_MAX_REQUESTS = 20
CHAT_WINDOW_SECONDS = 60
_chat_limiter = SlidingWindowRateLimiter(CHAT_MAX_REQUESTS, CHAT_WINDOW_SECONDS)


async def rate_limit_chat(current_user: Profile = Depends(get_current_user)) -> Profile:
    """FastAPI dependency: enforce the per-user chat rate limit, then hand back
    the authenticated user (so endpoints can keep using it as before)."""
    _chat_limiter.check(current_user.id)
    return current_user
