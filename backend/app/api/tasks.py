from uuid import UUID
from fastapi import APIRouter, HTTPException, status, Query

from app.api.deps import DbSession, CurrentUser
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse, TaskListResponse
from app.services.task import TaskService

router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.get("", response_model=TaskListResponse)
async def list_tasks(
    db: DbSession,
    current_user: CurrentUser,
    is_completed: bool | None = Query(None, description="Filter by completion status"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    service = TaskService(db)
    tasks, total = await service.list_tasks(
        user_id=current_user.id,
        is_completed=is_completed,
        limit=limit,
        offset=offset,
    )
    return TaskListResponse(
        tasks=[TaskResponse.model_validate(t) for t in tasks],
        total=total,
    )

@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    db: DbSession,
    current_user: CurrentUser,
):
    service = TaskService(db)
    task = await service.create(current_user.id, task_data)
    return TaskResponse.model_validate(task)

@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
):
    service = TaskService(db)
    task = await service.get_by_id(task_id, current_user.id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    return TaskResponse.model_validate(task)

@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: UUID,
    task_data: TaskUpdate,
    db: DbSession,
    current_user: CurrentUser,
):
    service = TaskService(db)
    task = await service.update(task_id, current_user.id, task_data)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    return TaskResponse.model_validate(task)

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
):
    service = TaskService(db)
    deleted = await service.delete(task_id, current_user.id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
