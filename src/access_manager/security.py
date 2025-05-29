from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from src.access_manager import crud
from src.access_manager.core.config import settings
from src.access_manager.db import get_db
from src.access_manager.models import User as UserModel

# --- Password hashing ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


# --- JWT settings ---
SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes


def create_access_token(
    data: Dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    expire = now + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login/token")


class TokenData(BaseModel):
    sub: Optional[str] = None


async def decode_access_token(token: str) -> Dict[str, Any]:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # validate payload structure
        TokenData(**payload)
        return payload
    except (JWTError, ValidationError):
        raise credentials_exception


# --- Новая зависимость: текущий активный пользователь ---


async def get_current_user_from_payload(
    payload: Dict[str, Any], db: AsyncSession
) -> Optional[UserModel]:
    sub = payload.get("sub")
    if sub is None:
        return None
    try:
        user_id = int(sub)
    except ValueError:
        return None
    return await crud.get_user(db, user_id)


async def get_current_active_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> UserModel:
    # 1) Декодируем и валидируем токен
    payload = await decode_access_token(token)
    # 2) Загружаем пользователя
    user = await get_current_user_from_payload(payload, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # 3) Проверяем активность
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    return user


def require_permission(*permission_names: str):
    """
    Возвращает зависимость, которая проверяет,
    что у current_user есть хотя бы одно из перечисленных имен разрешений.
    """

    async def dependency(
        current_user: UserModel = Depends(get_current_active_user),
    ) -> UserModel:
        # Собираем имена всех разрешений пользователя через его роли
        user_perms = {
            perm.name for role in current_user.roles for perm in role.permissions
        }
        # Проверяем наличие хотя бы одного требуемого
        if not any(name in user_perms for name in permission_names):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission(s) {permission_names} required",
            )
        return current_user

    return dependency
