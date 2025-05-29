# tests/test_users.py
from uuid import uuid4

import pytest


@pytest.mark.anyio
async def test_user_crud(client, auth_header):
    # ——— CREATE ———
    payload = {
        "username": f"alice_{uuid4().hex[:6]}",
        "email": f"alice_{uuid4().hex[:6]}@example.com",
        "password": "VerySecret123!",
        "role_ids": [],
    }
    r = await client.post("/users/", json=payload, headers=auth_header)
    assert r.status_code == 201, r.text
    created = r.json()
    user_id = created["id"]
    assert created["username"] == payload["username"]

    # ——— READ LIST ———
    r = await client.get("/users/", headers=auth_header)
    assert r.status_code == 200 and any(u["id"] == user_id for u in r.json())

    # ——— READ ONE ———
    r = await client.get(f"/users/{user_id}", headers=auth_header)
    assert r.status_code == 200 and r.json()["email"] == payload["email"]

    # ——— UPDATE ———
    r = await client.put(
        f"/users/{user_id}",
        json={"is_active": False},
        headers=auth_header,
    )
    assert r.status_code == 200 and r.json()["is_active"] is False

    # ——— DELETE ———
    r = await client.delete(f"/users/{user_id}", headers=auth_header)
    assert r.status_code == 200 and r.json()["id"] == user_id

    # Проверяем, что после удаления 404
    r = await client.get(f"/users/{user_id}", headers=auth_header)
    assert r.status_code == 404
