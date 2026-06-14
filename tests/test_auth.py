import pytest

@pytest.mark.asyncio
async def test_login_success(client):
    response = await client.post("/auth/login", json={"username": "user", "password": "userpass"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_fail(client):
    response = await client.post("/auth/login", json={"username": "user", "password": "wrong"})
    assert response.status_code == 401