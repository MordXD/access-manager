from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from . import crud, schemas
from .db import get_db

app = FastAPI(title="Access Manager API")


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
