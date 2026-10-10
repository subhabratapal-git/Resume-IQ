import time
from collections import defaultdict
from threading import Lock
from fastapi import HTTPException, Request, status


class SimpleRateLimiter:
    """
    Thread-safe in-memory sliding window rate limiter.
    Keyed by client IP address.
    """

    def __init__(self, max_requests: int, window_seconds: int, name: str = "endpoint"):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.name = name
        self.requests = defaultdict(list)
        self.lock = Lock()

    def check(self, request: Request):
        # Extract client IP (handle proxies if X-Forwarded-For is present)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            client_ip = forwarded.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "unknown"

        now = time.time()
        cutoff = now - self.window_seconds

        with self.lock:
            # Clean up timestamps older than window
            timestamps = [ts for ts in self.requests[client_ip] if ts > cutoff]
            if len(timestamps) >= self.max_requests:
                retry_after = int(self.window_seconds - (now - timestamps[0])) + 1
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Too many requests. Please try again in {retry_after} seconds.",
                    headers={"Retry-After": str(retry_after)},
                )

            timestamps.append(now)
            self.requests[client_ip] = timestamps


# Pre-configured rate limiters
login_limiter = SimpleRateLimiter(max_requests=10, window_seconds=60, name="login")
register_limiter = SimpleRateLimiter(max_requests=10, window_seconds=300, name="register")
password_change_limiter = SimpleRateLimiter(max_requests=5, window_seconds=60, name="change_password")
analyze_limiter = SimpleRateLimiter(max_requests=30, window_seconds=60, name="analyze")
