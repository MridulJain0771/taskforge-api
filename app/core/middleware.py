import hashlib
import time
import uuid

from fastapi import Request
from fastapi.responses import JSONResponse
from redis.asyncio import Redis
from redis.exceptions import RedisError
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings


class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith("/health"):
            return await call_next(request)

        identity = request.client.host if request.client else "unknown"
        auth = request.headers.get("authorization")
        if auth:
            identity = f"auth:{hashlib.sha256(auth.encode()).hexdigest()}"

        bucket = int(time.time() // 60)
        key = f"rate:{identity}:{bucket}"
        redis: Redis = request.app.state.redis

        try:
            count = await redis.incr(key)
            if count == 1:
                await redis.expire(key, 65)
            if count > settings.rate_limit_per_minute:
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Rate limit exceeded"},
                    headers={"Retry-After": "60"},
                )
        except RedisError:
            # Rate limiting is intentionally fail-open if Redis is unavailable.
            pass

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(settings.rate_limit_per_minute)
        return response
