# src/access_manager/crud.py

from typing import List, Optional
from datetime import timedelta

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from .models import User, Role, Permission
from .schemas import (
    UserCreate, UserUpdate,
    RoleCreate, RoleUpdate,
    PermissionCreate, PermissionUpdate,
)
from src.access_manager.security import get_password_hash


# ——— USER ———

async def get_user(db: AsyncSession, user_id: int) -> Optional[User]:
    result = await db.execute(
        select(User)
        .options(
            joinedload(User.roles).joinedload(Role.permissions)
        )
        .where(User.id == user_id)
    )
    return result.scalar_one_or_none()


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    result = await db.execute(
        select(User)
        .where(User.username == username)
    )
    return result.scalar_one_or_none()


async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[User]:
    result = await db.execute(
        select(User)
        .options(joinedload(User.roles))
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


async def create_user(db: AsyncSession, data: UserCreate) -> User:
    # hash password
    hashed = get_password_hash(data.password)
    user = User(
        username=data.username,
        email=data.email,
        hashed_password=hashed,
    )
    if data.role_ids:
        q = await db.execute(select(Role).where(Role.id.in_(data.role_ids)))
        user.roles = q.scalars().all()

    db.add(user)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with given username or email already exists."
        )

    # reload with eager relationships
    result = await db.execute(
        select(User)
        .options(joinedload(User.roles).joinedload(Role.permissions))
        .where(User.id == user.id)
    )
    return result.scalar_one()


async def update_user(db: AsyncSession, user_id: int, data: UserUpdate) -> Optional[User]:
    user = await get_user(db, user_id)
    if not user:
        return None

    for field, value in data.dict(exclude_unset=True).items():
        if field == "password":
            setattr(user, "hashed_password", get_password_hash(value))
        elif field == "role_ids":
            q = await db.execute(select(Role).where(Role.id.in_(value)))
            user.roles = q.scalars().all()
        else:
            setattr(user, field, value)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Update conflict: fields must be unique."
        )

    # reload with eager relationships
    result = await db.execute(
        select(User)
        .options(joinedload(User.roles).joinedload(Role.permissions))
        .where(User.id == user.id)
    )
    return result.scalar_one()


async def delete_user(db: AsyncSession, user_id: int) -> Optional[User]:
    user = await get_user(db, user_id)
    if not user:
        return None
    await db.delete(user)
    await db.commit()
    return user


# ——— ROLE ———

async def get_role(db: AsyncSession, role_id: int) -> Optional[Role]:
    result = await db.execute(
        select(Role)
        .options(joinedload(Role.permissions))
        .where(Role.id == role_id)
    )
    return result.scalar_one_or_none()


async def get_roles(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Role]:
    result = await db.execute(
        select(Role)
        .options(joinedload(Role.permissions))
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


async def create_role(db: AsyncSession, data: RoleCreate) -> Role:
    role = Role(name=data.name, description=data.description or "")
    if data.permission_ids:
        q = await db.execute(select(Permission).where(Permission.id.in_(data.permission_ids)))
        role.permissions = q.scalars().all()

    db.add(role)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role with given name already exists."
        )

    result = await db.execute(
        select(Role)
        .options(joinedload(Role.permissions))
        .where(Role.id == role.id)
    )
    return result.scalar_one()


async def update_role(db: AsyncSession, role_id: int, data: RoleUpdate) -> Optional[Role]:
    role = await get_role(db, role_id)
    if not role:
        return None

    for field, value in data.dict(exclude_unset=True).items():
        if field == "permission_ids":
            q = await db.execute(select(Permission).where(Permission.id.in_(value)))
            role.permissions = q.scalars().all()
        else:
            setattr(role, field, value)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Update conflict: fields must be unique."
        )

    result = await db.execute(
        select(Role)
        .options(joinedload(Role.permissions))
        .where(Role.id == role.id)
    )
    return result.scalar_one()


async def delete_role(db: AsyncSession, role_id: int) -> Optional[Role]:
    role = await get_role(db, role_id)
    if not role:
        return None
    await db.delete(role)
    await db.commit()
    return role


# ——— PERMISSION ———

async def get_permission(db: AsyncSession, perm_id: int) -> Optional[Permission]:
    result = await db.execute(
        select(Permission)
        .where(Permission.id == perm_id)
    )
    return result.scalar_one_or_none()


async def get_permissions(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Permission]:
    result = await db.execute(
        select(Permission)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


async def create_permission(db: AsyncSession, data: PermissionCreate) -> Permission:
    perm = Permission(name=data.name, description=data.description or "")
    db.add(perm)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Permission with given name already exists."
        )

    result = await db.execute(
        select(Permission)
        .where(Permission.id == perm.id)
    )
    return result.scalar_one()


async def update_permission(db: AsyncSession, perm_id: int, data: PermissionUpdate) -> Optional[Permission]:
    perm = await get_permission(db, perm_id)
    if not perm:
        return None

    for field, value in data.dict(exclude_unset=True).items():
        setattr(perm, field, value)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Update conflict: fields must be unique."
        )

    result = await db.execute(
        select(Permission)
        .where(Permission.id == perm.id)
    )
    return result.scalar_one()


async def delete_permission(db: AsyncSession, perm_id: int) -> Optional[Permission]:
    perm = await get_permission(db, perm_id)
    if not perm:
        return None
    await db.delete(perm)
    await db.commit()
    return perm
