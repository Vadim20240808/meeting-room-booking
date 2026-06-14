from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app import schemas, crud, models, auth
from app.database import get_session

router = APIRouter(prefix="/bookings", tags=["bookings"])

@router.post("", response_model=schemas.BookingOut)
async def create_booking(booking_data: schemas.BookingCreate,
                         db: AsyncSession = Depends(get_session),
                         current_user: models.User = Depends(auth.get_current_user)):
    room = await crud.get_room(db, booking_data.room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    slot = await crud.get_slot(db, booking_data.slot_id)
    if not slot or slot.room_id != booking_data.room_id:
        raise HTTPException(status_code=400, detail="Slot does not belong to this room")
    # Check if slot is free
    existing = await crud.get_active_booking_for_slot(db, booking_data.slot_id, booking_data.date)
    if existing:
        raise HTTPException(status_code=409, detail="Slot already booked for this date")
    booking = await crud.create_booking(db, current_user.id, booking_data.slot_id, booking_data.date)
    # Build response with room name and slot times
    return schemas.BookingOut(
        id=booking.id,
        user_id=booking.user_id,
        slot_id=booking.slot_id,
        date=booking.date,
        status=booking.status,
        room_name=room.name,
        start_time=slot.start_time,
        end_time=slot.end_time
    )

@router.delete("/{booking_id}", response_model=schemas.BookingOut)
async def cancel_booking(booking_id: int,
                         db: AsyncSession = Depends(get_session),
                         current_user: models.User = Depends(auth.get_current_user)):
    booking = await crud.get_booking(db, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.status == "cancelled":
        raise HTTPException(status_code=400, detail="Booking already cancelled")
    # User can cancel own; admin can cancel any
    if not current_user.is_admin and booking.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed to cancel this booking")
    # Capture related data before cancel (refresh loses eager-loaded relations)
    room_name = booking.slot.room.name
    slot_start = booking.slot.start_time
    slot_end = booking.slot.end_time
    booking = await crud.cancel_booking(db, booking)
    return schemas.BookingOut(
        id=booking.id,
        user_id=booking.user_id,
        slot_id=booking.slot_id,
        date=booking.date,
        status=booking.status,
        room_name=room_name,
        start_time=slot_start,
        end_time=slot_end
    )

@router.get("", response_model=list[schemas.BookingOut])
async def list_my_bookings(db: AsyncSession = Depends(get_session),
                           current_user: models.User = Depends(auth.get_current_user)):
    bookings = await crud.get_user_bookings(db, current_user.id)
    result = []
    for b in bookings:
        result.append(schemas.BookingOut(
            id=b.id,
            user_id=b.user_id,
            slot_id=b.slot_id,
            date=b.date,
            status=b.status,
            room_name=b.slot.room.name,
            start_time=b.slot.start_time,
            end_time=b.slot.end_time
        ))
    return result