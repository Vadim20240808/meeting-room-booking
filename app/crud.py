from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date
from sqlalchemy.orm import selectinload
from . import models, schemas
from .security import get_password_hash

# ... далее все функции без изменений

# Users
async def create_user(db: AsyncSession, username: str, password: str, is_admin: bool = False):
    hashed = get_password_hash(password)
    user = models.User(username=username, hashed_password=hashed, is_admin=is_admin)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

async def get_user_by_username(db: AsyncSession, username: str):
    result = await db.execute(select(models.User).where(models.User.username == username))
    return result.scalar_one_or_none()

async def get_user_by_id(db: AsyncSession, user_id: int):
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    return result.scalar_one_or_none()

# Rooms
async def get_rooms(db: AsyncSession):
    result = await db.execute(
        select(models.Room).options(selectinload(models.Room.slots)).order_by(models.Room.id)
    )
    return result.scalars().all()

async def get_room(db: AsyncSession, room_id: int):
    result = await db.execute(select(models.Room).where(models.Room.id == room_id))
    return result.scalar_one_or_none()

# Slots
async def get_slots_by_room(db: AsyncSession, room_id: int):
    result = await db.execute(select(models.Slot).where(models.Slot.room_id == room_id).order_by(models.Slot.start_time))
    return result.scalars().all()

async def get_slot(db: AsyncSession, slot_id: int):
    result = await db.execute(select(models.Slot).where(models.Slot.id == slot_id))
    return result.scalar_one_or_none()

# Bookings
async def get_active_booking_for_slot(db: AsyncSession, slot_id: int, booking_date: date):
    result = await db.execute(
        select(models.Booking).where(
            and_(
                models.Booking.slot_id == slot_id,
                models.Booking.date == booking_date,
                models.Booking.status == "active"
            )
        )
    )
    return result.scalar_one_or_none()

async def create_booking(db: AsyncSession, user_id: int, slot_id: int, booking_date: date):
    booking = models.Booking(user_id=user_id, slot_id=slot_id, date=booking_date, status="active")
    db.add(booking)
    await db.commit()
    await db.refresh(booking)
    return booking

async def get_booking(db: AsyncSession, booking_id: int):
    result = await db.execute(
        select(models.Booking).where(models.Booking.id == booking_id)
        .options(selectinload(models.Booking.slot).selectinload(models.Slot.room))
    )
    return result.scalar_one_or_none()

async def cancel_booking(db: AsyncSession, booking: models.Booking):
    booking.status = "cancelled"
    await db.commit()
    await db.refresh(booking)
    return booking

async def get_user_bookings(db: AsyncSession, user_id: int):
    result = await db.execute(
        select(models.Booking).where(models.Booking.user_id == user_id)
        .options(selectinload(models.Booking.slot).selectinload(models.Slot.room))
        .order_by(models.Booking.date)
    )
    return result.scalars().all()