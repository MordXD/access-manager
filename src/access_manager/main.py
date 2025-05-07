from datetime import timedelta
from typing import Annotated

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from . import crud, schemas
from .db import get_db
from src.access_manager import security
from src.access_manager.core.config import settings

app = FastAPI(title="Access Manager API")


# Pydantic-модель для ответа
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
        data={"sub": str(user.id)}, expires_delta=expires
    )
    return {"access_token": token, "token_type": "bearer"}

# ——— USER эндпоинты ———

@app.post(
    "/users/",
    response_model=schemas.UserRead,
    status_code=status.HTTP_201_CREATED
)
async def create_user(
    payload: schemas.UserCreate,
    db: AsyncSession = Depends(get_db),
):
    return await crud.create_user(db, payload)


@app.get(
    "/users/{user_id}",
    response_model=schemas.UserRead
)
async def read_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    user = await crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    return user


@app.get(
    "/users/",
    response_model=list[schemas.UserRead]
)
async def read_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    return await crud.get_users(db, skip, limit)


@app.put(
    "/users/{user_id}",
    response_model=schemas.UserRead
)
async def update_user(
    user_id: int,
    payload: schemas.UserUpdate,
    db: AsyncSession = Depends(get_db),
):
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
    db: AsyncSession = Depends(get_db),
):
    user = await crud.delete_user(db, user_id)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    return user


# ——— ROLE эндпоинты ———

@app.post(
    "/roles/",
    response_model=schemas.RoleRead,
    status_code=status.HTTP_201_CREATED
)
async def create_role(
    payload: schemas.RoleCreate,
    db: AsyncSession = Depends(get_db),
):
    return await crud.create_role(db, payload)


@app.get(
    "/roles/{role_id}",
    response_model=schemas.RoleRead
)
async def read_role(
    role_id: int,
    db: AsyncSession = Depends(get_db),
):
    role = await crud.get_role(db, role_id)
    if not role:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Role not found")
    return role


@app.get(
    "/roles/",
    response_model=list[schemas.RoleRead]
)
async def read_roles(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    return await crud.get_roles(db, skip, limit)


@app.put(
    "/roles/{role_id}",
    response_model=schemas.RoleRead
)
async def update_role(
    role_id: int,
    payload: schemas.RoleUpdate,
    db: AsyncSession = Depends(get_db),
):
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
    db: AsyncSession = Depends(get_db),
):
    role = await crud.delete_role(db, role_id)
    if not role:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Role not found")
    return role


# ——— PERMISSION эндпоинты ———

@app.post(
    "/permissions/",
    response_model=schemas.PermissionRead,
    status_code=status.HTTP_201_CREATED
)
async def create_permission(
    payload: schemas.PermissionCreate,
    db: AsyncSession = Depends(get_db),
):
    return await crud.create_permission(db, payload)


@app.get(
    "/permissions/{perm_id}",
    response_model=schemas.PermissionRead
)
async def read_permission(
    perm_id: int,
    db: AsyncSession = Depends(get_db),
):
    perm = await crud.get_permission(db, perm_id)
    if not perm:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Permission not found")
    return perm


@app.get(
    "/permissions/",
    response_model=list[schemas.PermissionRead]
)
async def read_permissions(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    return await crud.get_permissions(db, skip, limit)


@app.put(
    "/permissions/{perm_id}",
    response_model=schemas.PermissionRead
)
async def update_permission(
    perm_id: int,
    payload: schemas.PermissionUpdate,
    db: AsyncSession = Depends(get_db),
):
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
    db: AsyncSession = Depends(get_db),
):
    perm = await crud.delete_permission(db, perm_id)
    if not perm:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Permission not found")
    return perm
