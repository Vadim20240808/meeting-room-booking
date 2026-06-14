import pytest
from datetime import date

@pytest.mark.asyncio
async def test_create_booking_user(client, user_token):
    today = date.today().isoformat()
    resp = await client.post("/bookings", json={"room_id": 1, "slot_id": 1, "date": today},
                             headers={"Authorization": f"Bearer {user_token}"})
    assert resp.status_code == 200
    booking = resp.json()
    assert booking["status"] == "active"
    assert booking["room_name"] == "Переговорная 1"

@pytest.mark.asyncio
async def test_double_booking_conflict(client, user_token):
    today = date.today().isoformat()
    await client.post("/bookings", json={"room_id": 1, "slot_id": 1, "date": today},
                      headers={"Authorization": f"Bearer {user_token}"})
    resp = await client.post("/bookings", json={"room_id": 1, "slot_id": 1, "date": today},
                             headers={"Authorization": f"Bearer {user_token}"})
    assert resp.status_code == 409

@pytest.mark.asyncio
async def test_cancel_own_booking(client, user_token):
    today = date.today().isoformat()
    create_resp = await client.post("/bookings", json={"room_id": 1, "slot_id": 1, "date": today},
                                    headers={"Authorization": f"Bearer {user_token}"})
    booking_id = create_resp.json()["id"]
    cancel_resp = await client.delete(f"/bookings/{booking_id}",
                                      headers={"Authorization": f"Bearer {user_token}"})
    assert cancel_resp.status_code == 200
    assert cancel_resp.json()["status"] == "cancelled"

@pytest.mark.asyncio
async def test_admin_cancel_any(client, admin_token, user_token):
    # user creates booking
    today = date.today().isoformat()
    create_resp = await client.post("/bookings", json={"room_id": 1, "slot_id": 1, "date": today},
                                    headers={"Authorization": f"Bearer {user_token}"})
    booking_id = create_resp.json()["id"]
    # admin cancels
    cancel_resp = await client.delete(f"/bookings/{booking_id}",
                                      headers={"Authorization": f"Bearer {admin_token}"})
    assert cancel_resp.status_code == 200
    assert cancel_resp.json()["status"] == "cancelled"

@pytest.mark.asyncio
async def test_user_cannot_cancel_other(client, user_token, admin_token):
    # admin creates booking
    today = date.today().isoformat()
    create_resp = await client.post("/bookings", json={"room_id": 1, "slot_id": 1, "date": today},
                                    headers={"Authorization": f"Bearer {admin_token}"})
    booking_id = create_resp.json()["id"]
    # user tries to cancel
    cancel_resp = await client.delete(f"/bookings/{booking_id}",
                                      headers={"Authorization": f"Bearer {user_token}"})
    assert cancel_resp.status_code == 403

@pytest.mark.asyncio
async def test_list_user_bookings(client, user_token):
    today = date.today().isoformat()
    await client.post("/bookings", json={"room_id": 1, "slot_id": 1, "date": today},
                      headers={"Authorization": f"Bearer {user_token}"})
    resp = await client.get("/bookings", headers={"Authorization": f"Bearer {user_token}"})
    assert resp.status_code == 200
    bookings = resp.json()
    assert len(bookings) == 1
    assert bookings[0]["user_id"] is not None