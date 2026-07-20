from datetime import UTC, datetime, timedelta

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError
from pwdlib import PasswordHash
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db.databases import async_get_db
from app.models.user import Department, User

password_hash = PasswordHash.recommended()
bearer_scheme = HTTPBearer(auto_error=False)
revoked_tokens: set[str] = set()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    try:
        return password_hash.verify(password, hashed_password)
    except Exception:
        return False


def create_access_token(user_id: int) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: AsyncSession = Depends(async_get_db),
) -> User:
    error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="인증 정보가 없거나 유효하지 않습니다.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None or credentials.credentials in revoked_tokens:
        raise error
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        user_id = int(payload["sub"])
    except (InvalidTokenError, KeyError, TypeError, ValueError):
        raise error
    user = await db.get(User, user_id)
    if user is None or not user.is_active:
        raise error
    return user


async def require_medical_user(user: User = Depends(get_current_user)) -> User:
    if user.department != Department.MEDICAL_TEAM:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="의료 실무진만 등록할 수 있습니다.")
    return user
