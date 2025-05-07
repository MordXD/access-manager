from __future__ import annotations
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, EmailStr


# ----------------------
# Permission Schemas
# ----------------------

class PermissionRead(BaseModel):
    id: int
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class PermissionCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=255)


class PermissionUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=255)


# ----------------------
# Role Schemas
# ----------------------

class RoleRead(BaseModel):
    id: int
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    permissions: List[PermissionRead] = []

    model_config = {
        "from_attributes": True
    }


class RoleCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    permission_ids: List[int] = Field(default_factory=list)


class RoleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    permission_ids: Optional[List[int]] = None


# ----------------------
# User Schemas
# ----------------------

class UserRead(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime
    roles: List[RoleRead] = []

    model_config = {
        "from_attributes": True
    }


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)
    is_active: bool = True
    is_superuser: bool = False
    role_ids: List[int] = Field(default_factory=list)


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=100)
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    # password обычно обновляется через отдельный endpoint
    role_ids: Optional[List[int]] = None


# ----------------------
# Forward refs (если потребуется)
# ----------------------

# Для Pydantic v2: вызываем model_rebuild() для всех моделей, имеющих вложенные схемы
PermissionRead.model_rebuild()
RoleRead.model_rebuild()
UserRead.model_rebuild()
