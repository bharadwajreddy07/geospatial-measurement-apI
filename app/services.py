from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Task, TaskStatus, User
from app.schemas import TaskCreate, TaskUpdate
from app.security import hash_password, verify_password


async def register_user(db: AsyncSession, email: str, password: str) -> User:
    if await db.scalar(select(User).where(User.email == email.lower())):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email is already registered")
    user = User(email=email.lower(), password_hash=hash_password(password))
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def authenticate_user(db: AsyncSession, email: str, password: str) -> User:
    user = await db.scalar(select(User).where(User.email == email.lower()))
    if user is None or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    return user


async def get_task(db: AsyncSession, user_id: UUID, task_id: UUID) -> Task:
    task = await db.scalar(select(Task).where(Task.id == task_id, Task.owner_id == user_id))
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


async def list_tasks(db: AsyncSession, user_id: UUID, page: int, page_size: int, task_status: TaskStatus | None, sort: str) -> tuple[list[Task], int]:
    filters = [Task.owner_id == user_id]
    if task_status:
        filters.append(Task.status == task_status)
    order_column = Task.created_at if sort == "created_at" else Task.due_date
    query = select(Task).where(*filters).order_by(order_column.desc().nullslast())
    total = await db.scalar(select(func.count()).select_from(Task).where(*filters)) or 0
    result = await db.scalars(query.offset((page - 1) * page_size).limit(page_size))
    return list(result), total


async def create_task(db: AsyncSession, user_id: UUID, data: TaskCreate) -> Task:
    task = Task(owner_id=user_id, **data.model_dump())
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


async def update_task(db: AsyncSession, task: Task, data: TaskUpdate) -> Task:
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(task, key, value)
    await db.commit()
    await db.refresh(task)
    return task


async def delete_task(db: AsyncSession, task: Task) -> None:
    await db.delete(task)
    await db.commit()