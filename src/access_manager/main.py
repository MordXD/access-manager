# src/access_manager/main.py

from datetime import timedelta
from typing import Annotated
import time
import psutil
import asyncio

from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from src.access_manager import crud, schemas
from src.access_manager.db import get_db
from src.access_manager import security
from src.access_manager.core.config import settings
from src.access_manager.models import User as UserModel

app = FastAPI(title="Access Manager API")

origins = ["http://localhost:3000"]

# Middleware для логирования времени запросов
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True, 
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health Check Endpoint
@app.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Проверка здоровья сервиса и его зависимостей.
    """
    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "version": "0.1.0",
        "checks": {}
    }
    
    # Проверка подключения к базе данных
    try:
        result = await db.execute(text("SELECT 1"))
        await result.fetchone()
        health_status["checks"]["database"] = {
            "status": "healthy",
            "response_time": time.time()
        }
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["checks"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
    
    # Проверка использования ресурсов
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        health_status["checks"]["resources"] = {
            "status": "healthy",
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "disk_percent": disk.percent
        }
        
        # Предупреждение при высоком использовании ресурсов
        if cpu_percent > 80 or memory.percent > 80 or disk.percent > 90:
            health_status["status"] = "degraded"
            health_status["checks"]["resources"]["status"] = "degraded"
            
    except Exception as e:
        health_status["checks"]["resources"] = {
            "status": "unhealthy",
            "error": str(e)
        }
    
    status_code = 200 if health_status["status"] in ["healthy", "degraded"] else 503
    return health_status

@app.get("/metrics")
async def get_metrics(db: AsyncSession = Depends(get_db)):
    """
    Метрики для мониторинга Prometheus.
    """
    try:
        # Получение базовых метрик
        users_count = await crud.get_users_count(db)
        roles_count = await crud.get_roles_count(db) 
        permissions_count = await crud.get_permissions_count(db)
        
        # Системные метрики
        cpu_usage = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        metrics = f"""# HELP access_manager_users_total Total number of users
# TYPE access_manager_users_total gauge
access_manager_users_total {users_count}

# HELP access_manager_roles_total Total number of roles
# TYPE access_manager_roles_total gauge
access_manager_roles_total {roles_count}

# HELP access_manager_permissions_total Total number of permissions
# TYPE access_manager_permissions_total gauge
access_manager_permissions_total {permissions_count}

# HELP access_manager_cpu_usage_percent CPU usage percentage
# TYPE access_manager_cpu_usage_percent gauge
access_manager_cpu_usage_percent {cpu_usage}

# HELP access_manager_memory_usage_percent Memory usage percentage
# TYPE access_manager_memory_usage_percent gauge
access_manager_memory_usage_percent {memory.percent}

# HELP access_manager_disk_usage_percent Disk usage percentage
# TYPE access_manager_disk_usage_percent gauge
access_manager_disk_usage_percent {disk.percent}
"""
        
        return metrics
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to collect metrics: {str(e)}"
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
#   РЕГИСТРАЦИЯ НОВОГО ПОЛЬЗОВАТЕЛЯ
# --------------------------------------

@app.post(
    "/register",
    response_model=schemas.UserRead,
    status_code=status.HTTP_201_CREATED
)
async def register_new_user(
    payload: schemas.UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Регистрация нового пользователя.
    Доступно без аутентификации.
    """
    return await crud.create_user(db, payload)


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
