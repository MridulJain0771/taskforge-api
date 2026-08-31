from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis.asyncio import Redis

from app.api.routes import auth, health, tasks, users
from app.core.config import settings
from app.core.logging import configure_logging
from app.core.middleware import RateLimitMiddleware, RequestIdMiddleware
from app.db.session import engine

configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Own async infrastructure resources for the lifetime of the application."""
    redis = Redis.from_url(settings.redis_url, decode_responses=True)
    app.state.redis = redis
    try:
        yield
    finally:
        await redis.aclose()
        await engine.dispose()


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description=(
        "Production-style FastAPI backend showcasing auth, PostgreSQL, Redis, "
        "Celery, Docker and CI."
    ),
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(RequestIdMiddleware)

app.include_router(health.router)
app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(tasks.router, prefix="/api/v1")
