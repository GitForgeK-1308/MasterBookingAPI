import uuid
from datetime import datetime, date, time
from src.bookings.models import BookingStatus
from pydantic import BaseModel, ConfigDict



class BookingCreate(BaseModel):
    offering_id: uuid.UUID
    booking_date: date
    start_time: time
    client_name: str
    client_phone: str
    client_email: str | None = None



class BookingStatusUpdate(BaseModel):
    status: BookingStatus


class BookingResponse(BaseModel):
    
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    master_id: uuid.UUID
    offering_id: uuid.UUID

    booking_date: date
    start_time: time
    end_time: time

    client_name: str
    client_phone: str
    client_email: str | None

    status: BookingStatus
    created_at: datetime


class AvailableSlotsResponse(BaseModel):
    master_id: uuid.UUID
    offering_id: uuid.UUID
    booking_date: date
    slots: list[time]