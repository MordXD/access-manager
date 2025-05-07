# tests/test_auth.py
import pytest
from uuid import uuid4

from src.access_manager.models import User
from src.access_manager.security import get_password_hash


@pytest.mark.anyio
async def test_login_success(client, db):
    """
    /login/token → 200 + токен, если пара логин/пароль верна.
    """
    username = f"user_{uuid4().hex[:8]}"
    password = "secretPass123"
    db.add(
        User(
            username=username,
            email=f"{username}@example.com",
            hashed_password=get_password_hash(password),
            is_active=True,
        )
    )
    await db.commit()

    resp = await client.post(
        "/login/token",
        data={"username": username, "password": password},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["token_type"] == "bearer"
    assert isinstance(data["access_token"], str) and len(data["access_token"]) > 20


@pytest.mark.anyio
async def test_login_wrong_password(client, db):
    username = f"user_{uuid4().hex[:8]}"
    db.add(
        User(
            username=username,
            email=f"{username}@example.com",
            hashed_password=get_password_hash("correct_password"),
            is_active=True,
        )
    )
    await db.commit()

    resp = await client.post(
        "/login/token",
        data={"username": username, "password": "wrong_password"},
    )
    assert resp.status_code == 401
