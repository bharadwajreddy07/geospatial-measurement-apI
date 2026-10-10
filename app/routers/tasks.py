from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status

from app.dependencies import CurrentUser, DbSession
from app.models import TaskStatus
from app.schemas import PaginatedTasks, TaskCreate, TaskResponse, TaskUpdate
from app.services import create_task, delete_task, get_task, list_tasks, update_task

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("", response_model=PaginatedTasks)
async def get_tasks(
    db: DbSession,
    user: CurrentUser,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    task_status: TaskStatus | None = Query(default=None, alias="status"),
    sort: str = Query("created_at", pattern="^(created_at|due_date)$"),
) -> PaginatedTasks:
    items, total = await list_tasks(db, user.id, page, page_size, task_status, sort)
    return PaginatedTasks(items=items, page=page, page_size=page_size, total=total)


@router.post("", response_model=TaskResponse, status_code=201)
async def post_task(payload: TaskCreate, db: DbSession, user: CurrentUser) -> TaskResponse:
    return await create_task(db, user.id, payload)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_one_task(task_id: UUID, db: DbSession, user: CurrentUser) -> TaskResponse:
    return await get_task(db, user.id, task_id)


@router.put("/{task_id}", response_model=TaskResponse)
async def put_task(task_id: UUID, payload: TaskUpdate, db: DbSession, user: CurrentUser) -> TaskResponse:
    task = await get_task(db, user.id, task_id)
    return await update_task(db, task, payload)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_task(task_id: UUID, db: DbSession, user: CurrentUser) -> Response:
    task = await get_task(db, user.id, task_id)
    await delete_task(db, task)
    return Response(status_code=status.HTTP_204_NO_CONTENT)