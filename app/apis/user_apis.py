from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import HTTPAuthorizationCredentials, OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import (
    bearer_scheme,
    create_access_token,
    get_current_user,
    revoked_tokens,
    verify_password,
)
from app.core.db.databases import async_get_db
from app.models.user import User

router = APIRouter(prefix="/api/v1/users", tags=["users"])


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/login", response_model=TokenResponse)
async def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(async_get_db),
):
    user = await db.scalar(select(User).where(User.email == form.username))
    if user is None or not verify_password(form.password, user.password):
        raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 올바르지 않습니다.")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="비활성화된 사용자입니다.")
    return TokenResponse(access_token=create_access_token(user.id))


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    _: User = Depends(get_current_user),
):
    revoked_tokens.add(credentials.credentials)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
