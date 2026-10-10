from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models import TaskStatus


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: EmailStr
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(UserCreate):
    pass


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=5000)
    status: TaskStatus = TaskStatus.pending
    due_date: datetime | None = None

    @field_validator("title", "description")
    @classmethod
    def strip_text(cls, value: str | None) -> str | None:
        return value.strip() if value is not None else value


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=5000)
    status: TaskStatus | None = None
    due_date: datetime | None = None

    @field_validator("title", "description")
    @classmethod
    def strip_text(cls, value: str | None) -> str | None:
        return value.strip() if value is not None else value


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    description: str | None
    status: TaskStatus
    due_date: datetime | None
    created_at: datetime
    updated_at: datetime


class PaginatedTasks(BaseModel):
    items: list[TaskResponse]
    page: int
    page_size: int
    total: int