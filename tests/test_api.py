import pytest


@pytest.mark.asyncio
async def test_auth_and_task_lifecycle(client):
    response = await client.post("/auth/register", json={"email": "user@example.com", "password": "password123"})
    assert response.status_code == 201

    response = await client.post("/auth/login", data={"username": "user@example.com", "password": "password123"})
    assert response.status_code == 200
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.post("/tasks", json={"title": "Ship API"}, headers=headers)
    assert response.status_code == 201
    task_id = response.json()["id"]

    response = await client.get("/tasks?page=1&page_size=10&status=pending", headers=headers)
    assert response.status_code == 200
    assert response.json()["total"] == 1

    response = await client.put(f"/tasks/{task_id}", json={"status": "completed"}, headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == "completed"

    response = await client.delete(f"/tasks/{task_id}", headers=headers)
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_validation_and_auth_errors(client):
    response = await client.post("/auth/register", json={"email": "bad", "password": "short"})
    assert response.status_code == 422
    response = await client.get("/tasks")
    assert response.status_code == 401