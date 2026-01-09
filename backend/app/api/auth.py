from fastapi import APIRouter, HTTPException, status, Response, Cookie
from typing import Annotated

from app.api.deps import DbSession, CurrentUser
from app.schemas.user import UserCreate, UserResponse, LoginRequest, AuthResponse, TokenRefreshResponse
from app.services.auth import (
    create_user,
    get_user_by_email,
    authenticate_user,
    update_last_login,
    create_access_token,
    generate_refresh_token,
    create_refresh_token_record,
    validate_refresh_token,
    revoke_refresh_token,
    revoke_all_user_tokens,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, response: Response, db: DbSession):
    existing_user = await get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    user = await create_user(db, user_data.email, user_data.password)
    await update_last_login(db, user)

    access_token = create_access_token(
        {"sub": str(user.id), "email": user.email, "role": user.role.value}
    )

    refresh_token = generate_refresh_token()
    await create_refresh_token_record(db, user.id, refresh_token)

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=60 * 60 * 24 * 7,  # 7 days
    )

    return AuthResponse(
        access_token=access_token,
        user=UserResponse.model_validate(user),
    )

@router.post("/login", response_model=AuthResponse)
async def login(login_data: LoginRequest, response: Response, db: DbSession):
    user = await authenticate_user(db, login_data.email, login_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated",
        )

    await update_last_login(db, user)

    access_token = create_access_token(
        {"sub": str(user.id), "email": user.email, "role": user.role.value}
    )

    refresh_token = generate_refresh_token()
    await create_refresh_token_record(db, user.id, refresh_token)

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=60 * 60 * 24 * 7,
    )

    return AuthResponse(
        access_token=access_token,
        user=UserResponse.model_validate(user),
    )

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    response: Response,
    current_user: CurrentUser,
    db: DbSession,
    refresh_token: Annotated[str | None, Cookie()] = None,
):
    if refresh_token:
        await revoke_refresh_token(db, refresh_token)

    response.delete_cookie("refresh_token")

@router.post("/refresh", response_model=TokenRefreshResponse)
async def refresh_access_token(
    response: Response,
    db: DbSession,
    refresh_token: Annotated[str | None, Cookie()] = None,
):
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token required",
        )

    token_record = await validate_refresh_token(db, refresh_token)
    if not token_record:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    from app.services.auth import get_user_by_id
    user = await get_user_by_id(db, token_record.user_id)

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    # Revoke old token and create new one (rotation)
    await revoke_refresh_token(db, refresh_token)
    new_refresh_token = generate_refresh_token()
    await create_refresh_token_record(db, user.id, new_refresh_token)

    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=60 * 60 * 24 * 7,
    )

    access_token = create_access_token(
        {"sub": str(user.id), "email": user.email, "role": user.role.value}
    )

    return TokenRefreshResponse(access_token=access_token)

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: CurrentUser):
    return UserResponse.model_validate(current_user)
