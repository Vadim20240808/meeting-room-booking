from pydantic import BaseModel
from datetime import date, time
from typing import List, Optional

# Auth
class Token(BaseModel):
    access_token: str
    token_type: str

class LoginData(BaseModel):
    username: str
    password: str

# Rooms & slots
class SlotOut(BaseModel):
    id: int
    start_time: time
    end_time: time

    class Config:
        from_attributes = True

class RoomOut(BaseModel):
    id: int
    name: str
    slots: List[SlotOut] = []

    class Config:
        from_attributes = True

class RoomAvailabilitySlot(BaseModel):
    slot_id: int
    start_time: time
    end_time: time
    available: bool

class RoomAvailability(BaseModel):
    room_id: int
    room_name: str
    date: date
    slots: List[RoomAvailabilitySlot]

# Bookings
class BookingCreate(BaseModel):
    room_id: int
    slot_id: int
    date: date

class BookingOut(BaseModel):
    id: int
    user_id: int
    slot_id: int
    date: date
    status: str
    room_name: Optional[str] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None

    class Config:
        from_attributes = True