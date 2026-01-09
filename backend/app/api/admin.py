from uuid import UUID
from fastapi import APIRouter, HTTPException, status, Query

from app.api.deps import DbSession, AdminUser
from app.schemas.admin import AdminUserResponse, AdminUserListResponse, UserStatusUpdate
from app.services.admin import AdminService

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/users", response_model=AdminUserListResponse)
async def list_users(
    db: DbSession,
    admin: AdminUser,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    service = AdminService(db)
    users, total = await service.list_users(limit=limit, offset=offset)
    return AdminUserListResponse(
        users=[AdminUserResponse(**u) for u in users],
        total=total,
    )

@router.get("/users/{user_id}", response_model=AdminUserResponse)
async def get_user(
    user_id: UUID,
    db: DbSession,
    admin: AdminUser,
):
    service = AdminService(db)
    user = await service.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return AdminUserResponse(**user)

@router.patch("/users/{user_id}", response_model=AdminUserResponse)
async def update_user_status(
    user_id: UUID,
    update_data: UserStatusUpdate,
    db: DbSession,
    admin: AdminUser,
):
    # Prevent admin from deactivating themselves
    if user_id == admin.id and not update_data.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account",
        )

    service = AdminService(db)
    user = await service.update_user_status(user_id, update_data.is_active)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return AdminUserResponse(**user)
