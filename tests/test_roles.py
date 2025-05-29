# tests/test_roles.py
from uuid import uuid4

import pytest
from sqlalchemy import select

from src.access_manager.models import Permission


@pytest.mark.anyio
async def test_role_crud(client, db, auth_header):
    # Подготовим разрешение, к которому будет привязана роль
    perm_name = f"perm_{uuid4().hex[:6]}"
    perm = Permission(name=perm_name, description="test-perm")
    db.add(perm)
    await db.commit()
    perm_id = perm.id

    # ───── CREATE ─────
    payload = {
        "name": f"role_{uuid4().hex[:6]}",
        "description": "role-for-tests",
        "permission_ids": [perm_id],
    }
    r = await client.post("/roles/", json=payload, headers=auth_header)
    assert r.status_code == 201, r.text
    role = r.json()
    role_id = role["id"]
    assert role["permissions"][0]["name"] == perm_name

    # ───── READ ─────
    r = await client.get(f"/roles/{role_id}", headers=auth_header)
    assert r.status_code == 200 and r.json()["id"] == role_id

    # ───── UPDATE ─────
    r = await client.put(
        f"/roles/{role_id}",
        json={"description": "updated-desc"},
        headers=auth_header,
    )
    assert r.status_code == 200 and r.json()["description"] == "updated-desc"

    # ───── DELETE ─────
    r = await client.delete(f"/roles/{role_id}", headers=auth_header)
    assert r.status_code == 200

    # Доп. проверка: роли больше нет в БД
    q = await db.execute(select(Permission).where(Permission.id == perm_id))
    assert q.scalar_one() is not None  # разрешение остаётся
