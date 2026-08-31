import asyncio
import logging

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.task import Task, TaskStatus
from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


async def _process_task(task_id: int) -> dict[str, str | int]:
    async with SessionLocal() as db:
        result = await db.execute(select(Task).where(Task.id == task_id))
        task = result.scalar_one_or_none()
        if task is None:
            return {"task_id": task_id, "status": "not_found"}
        task.status = TaskStatus.PROCESSING
        await db.commit()
        try:
            await asyncio.sleep(0.25)
            task.status = TaskStatus.COMPLETED
            await db.commit()
            logger.info("background task completed", extra={"task_id": task_id})
            return {"task_id": task_id, "status": "completed"}
        except Exception:
            task.status = TaskStatus.FAILED
            await db.commit()
            raise


@celery_app.task(name="taskforge.process_task", bind=True, max_retries=3)
def process_task(self, task_id: int):
    try:
        return asyncio.run(_process_task(task_id))
    except Exception as exc:
        raise self.retry(exc=exc, countdown=min(2**self.request.retries, 30)) from exc
