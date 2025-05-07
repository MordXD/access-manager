# tests/test_permissions.py
import pytest
from uuid import uuid4


@pytest.mark.anyio
async def test_permission_crud(client, auth_header):
    # ───── CREATE ─────
    name = f"edit_{uuid4().hex[:6]}"
    r = await client.post(
        "/permissions/",
        json={"name": name, "description": "desc"},
        headers=auth_header,
    )
    assert r.status_code == 201, r.text
    perm = r.json()
    perm_id = perm["id"]

    # ───── READ LIST ─────
    r = await client.get("/permissions/", headers=auth_header)
    assert r.status_code == 200
    assert any(p["id"] == perm_id for p in r.json())

    # ───── UPDATE ─────
    r = await client.put(
        f"/permissions/{perm_id}",
        json={"description": "new-desc"},
        headers=auth_header,
    )
    assert r.status_code == 200 and r.json()["description"] == "new-desc"

    # ───── DELETE ─────
    r = await client.delete(f"/permissions/{perm_id}", headers=auth_header)
    assert r.status_code == 200

    # Проверяем, что после удаления возвращается 404
    r = await client.get(f"/permissions/{perm_id}", headers=auth_header)
    assert r.status_code == 404
