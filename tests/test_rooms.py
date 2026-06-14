import pytest
from datetime import date

@pytest.mark.asyncio
async def test_list_rooms_unauthorized(client):
    response = await client.get("/rooms")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_list_rooms_user(client, user_token):
    response = await client.get("/rooms", headers={"Authorization": f"Bearer {user_token}"})
    assert response.status_code == 200
    rooms = response.json()
    assert len(rooms) == 2
    assert rooms[0]["name"] == "Переговорная 1"

@pytest.mark.asyncio
async def test_room_availability(client, user_token):
    today = date.today().isoformat()
    response = await client.get(f"/rooms/1/availability?date={today}",
                                headers={"Authorization": f"Bearer {user_token}"})
    assert response.status_code == 200
    data = response.json()
    assert len(data["slots"]) == 2
    assert all(slot["available"] for slot in data["slots"])