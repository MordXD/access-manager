# src/access_manager/main.py

from datetime import timedelta
from typing import Annotated

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.middleware.cors import CORSMiddleware

from src.access_manager import crud, schemas
from src.access_manager.db import get_db
from src.access_manager import security
from src.access_manager.core.config import settings
from src.access_manager.models import User as UserModel

app = FastAPI(title="Access Manager API")

origins = ["http://localhost:3000"]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True, 
    allow_methods=["*"],
    allow_headers=["*"],
)
# --------------------------------------
#   AUTH: получение и проверка токена
# --------------------------------------

class TokenResponse(schemas.BaseModel):
    access_token: str
    token_type: str = "bearer"


@app.post("/login/token", response_model=TokenResponse)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncSession = Depends(get_db),
):
    user = await crud.get_user_by_username(db, form_data.username)
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    expires = timedelta(minutes=settings.access_token_expire_minutes)
    token = security.create_access_token(
        data={"sub": str(user.id)},
        expires_delta=expires
    )
    return {"access_token": token, "token_type": "bearer"}


# --------------------------------------
#   ЗАЩИЩЕННЫЕ ЭНДПОИНТЫ
# --------------------------------------

@app.get("/users/me", response_model=schemas.UserRead)
async def read_users_me(
    current_user: UserModel = Depends(security.get_current_active_user),
):
    """
    Информация о текущем аутентифицированном и активном пользователе.
    """
    return current_user


@app.post(
    "/users/",
    response_model=schemas.UserRead,
    status_code=status.HTTP_201_CREATED
)
async def create_user(
    payload: schemas.UserCreate,
    current_user: UserModel = Depends(security.require_permission("create_user")),
    db: AsyncSession = Depends(get_db),
):
    """
    Создание нового пользователя.
    Требуется разрешение "create_user".
    """
    return await crud.create_user(db, payload)


@app.get(
    "/users/{user_id}",
    response_model=schemas.UserRead
)
async def read_user(
    user_id: int,
    current_user: UserModel = Depends(security.require_permission("read_user")),
    db: AsyncSession = Depends(get_db),
):
    """
    Получение пользователя по ID.
    Требуется разрешение "read_user".
    """
    user = await crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    return user


@app.get(
    "/users/",
    response_model=list[schemas.UserRead]
)
async def read_users(
    current_user: UserModel = Depends(security.require_permission("read_user")),
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """
    Список пользователей.
    Требуется разрешение "read_user".
    """
    return await crud.get_users(db, skip, limit)


@app.put(
    "/users/{user_id}",
    response_model=schemas.UserRead
)
async def update_user(
    user_id: int,
    payload: schemas.UserUpdate,
    current_user: UserModel = Depends(security.require_permission("update_user")),
    db: AsyncSession = Depends(get_db),
):
    """
    Обновление пользователя по ID.
    Требуется разрешение "update_user".
    """
    user = await crud.update_user(db, user_id, payload)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    return user


@app.delete(
    "/users/{user_id}",
    response_model=schemas.UserRead
)
async def delete_user(
    user_id: int,
    current_user: UserModel = Depends(security.require_permission("delete_user")),
    db: AsyncSession = Depends(get_db),
):
    """
    Удаление пользователя по ID.
    Требуется разрешение "delete_user".
    """
    user = await crud.delete_user(db, user_id)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    return user


# --------------------------------------
#   ROLE эндпоинты
# --------------------------------------

@app.post(
    "/roles/",
    response_model=schemas.RoleRead,
    status_code=status.HTTP_201_CREATED
)
async def create_role(
    payload: schemas.RoleCreate,
    current_user: UserModel = Depends(security.require_permission("create_role")),
    db: AsyncSession = Depends(get_db),
):
    """
    Создание роли.
    Требуется разрешение "create_role".
    """
    return await crud.create_role(db, payload)


@app.get(
    "/roles/{role_id}",
    response_model=schemas.RoleRead
)
async def read_role(
    role_id: int,
    current_user: UserModel = Depends(security.require_permission("read_role")),
    db: AsyncSession = Depends(get_db),
):
    """
    Получение роли по ID.
    Требуется разрешение "read_role".
    """
    role = await crud.get_role(db, role_id)
    if not role:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Role not found")
    return role


@app.get(
    "/roles/",
    response_model=list[schemas.RoleRead]
)
async def read_roles(
    current_user: UserModel = Depends(security.require_permission("read_role")),
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """
    Список ролей.
    Требуется разрешение "read_role".
    """
    return await crud.get_roles(db, skip, limit)


@app.put(
    "/roles/{role_id}",
    response_model=schemas.RoleRead
)
async def update_role(
    role_id: int,
    payload: schemas.RoleUpdate,
    current_user: UserModel = Depends(security.require_permission("update_role")),
    db: AsyncSession = Depends(get_db),
):
    """
    Обновление роли по ID.
    Требуется разрешение "update_role".
    """
    role = await crud.update_role(db, role_id, payload)
    if not role:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Role not found")
    return role


@app.delete(
    "/roles/{role_id}",
    response_model=schemas.RoleRead
)
async def delete_role(
    role_id: int,
    current_user: UserModel = Depends(security.require_permission("delete_role")),
    db: AsyncSession = Depends(get_db),
):
    """
    Удаление роли по ID.
    Требуется разрешение "delete_role".
    """
    role = await crud.delete_role(db, role_id)
    if not role:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Role not found")
    return role


# --------------------------------------
#   PERMISSION эндпоинты
# --------------------------------------

@app.post(
    "/permissions/",
    response_model=schemas.PermissionRead,
    status_code=status.HTTP_201_CREATED
)
async def create_permission(
    payload: schemas.PermissionCreate,
    current_user: UserModel = Depends(security.require_permission("create_permission")),
    db: AsyncSession = Depends(get_db),
):
    """
    Создание разрешения.
    Требуется разрешение "create_permission".
    """
    return await crud.create_permission(db, payload)


@app.get(
    "/permissions/{perm_id}",
    response_model=schemas.PermissionRead
)
async def read_permission(
    perm_id: int,
    current_user: UserModel = Depends(security.require_permission("read_permission")),
    db: AsyncSession = Depends(get_db),
):
    """
    Получение разрешения по ID.
    Требуется разрешение "read_permission".
    """
    perm = await crud.get_permission(db, perm_id)
    if not perm:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Permission not found")
    return perm


@app.get(
    "/permissions/",
    response_model=list[schemas.PermissionRead]
)
async def read_permissions(
    current_user: UserModel = Depends(security.require_permission("read_permission")),
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """
    Список разрешений.
    Требуется разрешение "read_permission".
    """
    return await crud.get_permissions(db, skip, limit)


@app.put(
    "/permissions/{perm_id}",
    response_model=schemas.PermissionRead
)
async def update_permission(
    perm_id: int,
    payload: schemas.PermissionUpdate,
    current_user: UserModel = Depends(security.require_permission("update_permission")),
    db: AsyncSession = Depends(get_db),
):
    """
    Обновление разрешения по ID.
    Требуется разрешение "update_permission".
    """
    perm = await crud.update_permission(db, perm_id, payload)
    if not perm:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Permission not found")
    return perm


@app.delete(
    "/permissions/{perm_id}",
    response_model=schemas.PermissionRead
)
async def delete_permission(
    perm_id: int,
    current_user: UserModel = Depends(security.require_permission("delete_permission")),
    db: AsyncSession = Depends(get_db),
):
    """
    Удаление разрешения по ID.
    Требуется разрешение "delete_permission".
    """
    perm = await crud.delete_permission(db, perm_id)
    if not perm:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Permission not found")
    return perm
