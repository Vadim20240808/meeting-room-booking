from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date
from app import schemas, crud, models, auth
from app.database import get_session

router = APIRouter(prefix="/rooms", tags=["rooms"])

@router.get("", response_model=list[schemas.RoomOut])
async def list_rooms(db: AsyncSession = Depends(get_session),
                     current_user: models.User = Depends(auth.get_current_user)):
    rooms = await crud.get_rooms(db)
    return rooms

@router.get("/{room_id}/availability", response_model=schemas.RoomAvailability)
async def room_availability(room_id: int,
                            date_query: date = Query(..., alias="date"),
                            db: AsyncSession = Depends(get_session),
                            current_user: models.User = Depends(auth.get_current_user)):
    room = await crud.get_room(db, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    slots = await crud.get_slots_by_room(db, room_id)
    availability_slots = []
    for slot in slots:
        active_booking = await crud.get_active_booking_for_slot(db, slot.id, date_query)
        availability_slots.append(schemas.RoomAvailabilitySlot(
            slot_id=slot.id,
            start_time=slot.start_time,
            end_time=slot.end_time,
            available=active_booking is None
        ))
    return schemas.RoomAvailability(
        room_id=room.id,
        room_name=room.name,
        date=date_query,
        slots=availability_slots
    )