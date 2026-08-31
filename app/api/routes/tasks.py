from typing import Annotated

from fastapi import APIRouter, Header, HTTPException, Query, Response, status

from app.api.deps import CurrentUser, DbSession
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate
from app.services import tasks as task_service
from app.workers.tasks import process_task

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    payload: TaskCreate,
    db: DbSession,
    current_user: CurrentUser,
    response: Response,
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
) -> TaskResponse:
    task, created = await task_service.create_task(
        db, owner_id=current_user.id, payload=payload, idempotency_key=idempotency_key
    )
    if not created:
        response.status_code = status.HTTP_200_OK
        response.headers["X-Idempotent-Replay"] = "true"
    return TaskResponse.model_validate(task)


@router.get("", response_model=list[TaskResponse])
async def list_tasks(
    db: DbSession,
    current_user: CurrentUser,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> list[TaskResponse]:
    tasks = await task_service.list_tasks(db, owner_id=current_user.id, limit=limit, offset=offset)
    return [TaskResponse.model_validate(task) for task in tasks]


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int, db: DbSession, current_user: CurrentUser) -> TaskResponse:
    task = await task_service.get_task(db, owner_id=current_user.id, task_id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskResponse.model_validate(task)


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(task_id: int, payload: TaskUpdate, db: DbSession, current_user: CurrentUser) -> TaskResponse:
    task = await task_service.get_task(db, owner_id=current_user.id, task_id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task = await task_service.update_task(db, task, payload)
    return TaskResponse.model_validate(task)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: int, db: DbSession, current_user: CurrentUser) -> None:
    task = await task_service.get_task(db, owner_id=current_user.id, task_id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    await task_service.delete_task(db, task)


@router.post("/{task_id}/process", status_code=status.HTTP_202_ACCEPTED)
async def enqueue_task(task_id: int, db: DbSession, current_user: CurrentUser) -> dict[str, str]:
    task = await task_service.get_task(db, owner_id=current_user.id, task_id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    job = process_task.delay(task.id)
    return {"job_id": job.id, "status": "queued"}
