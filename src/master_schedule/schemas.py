import uuid
from src.master_schedule.models import WeekDay
from datetime import time
from pydantic import BaseModel, ConfigDict


class MasterScheduleBase(BaseModel):
    day_of_week: WeekDay 
    start_time: time | None = None
    end_time: time | None = None
    is_working: bool = True

class MasterScheduleCreate(MasterScheduleBase):
    pass


class MasterScheduleUpdate(BaseModel):
    day_of_week: WeekDay | None = None
    start_time: time | None = None
    end_time: time | None = None
    is_working: bool | None = None

class MasterScheduleResponse(MasterScheduleBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    master_id: uuid.UUID