from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

from app.models.user import UserRole

class AdminUserResponse(BaseModel):
    id: UUID
    email: str
    role: UserRole
    is_active: bool
    created_at: datetime
    last_login_at: datetime | None
    task_count: int

    class Config:
        from_attributes = True

class AdminUserListResponse(BaseModel):
    users: list[AdminUserResponse]
    total: int

class UserStatusUpdate(BaseModel):
    is_active: bool
