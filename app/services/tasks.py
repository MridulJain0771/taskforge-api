from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate


async def create_task(db: AsyncSession, *, owner_id: int, payload: TaskCreate, idempotency_key: str | None) -> tuple[Task, bool]:
    if idempotency_key:
        result = await db.execute(select(Task).where(Task.owner_id == owner_id, Task.idempotency_key == idempotency_key))
        existing = result.scalar_one_or_none()
        if existing:
            return existing, False
    task = Task(owner_id=owner_id, title=payload.title, description=payload.description, idempotency_key=idempotency_key)
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task, True


async def list_tasks(db: AsyncSession, *, owner_id: int, limit: int, offset: int) -> list[Task]:
    result = await db.execute(select(Task).where(Task.owner_id == owner_id).order_by(Task.id.desc()).limit(limit).offset(offset))
    return list(result.scalars().all())


async def get_task(db: AsyncSession, *, owner_id: int, task_id: int) -> Task | None:
    result = await db.execute(select(Task).where(Task.id == task_id, Task.owner_id == owner_id))
    return result.scalar_one_or_none()


async def update_task(db: AsyncSession, task: Task, payload: TaskUpdate) -> Task:
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    await db.commit()
    await db.refresh(task)
    return task


async def delete_task(db: AsyncSession, task: Task) -> None:
    await db.delete(task)
    await db.commit()
