from fastapi import APIRouter, HTTPException, Request
from sqlalchemy import text

from app.db.session import SessionLocal

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/live")
async def live() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready")
async def ready(request: Request) -> dict[str, str]:
    try:
        async with SessionLocal() as session:
            await session.execute(text("SELECT 1"))
        await request.app.state.redis.ping()
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Dependency check failed") from exc
    return {"status": "ready"}
