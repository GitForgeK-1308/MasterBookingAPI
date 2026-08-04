import uuid
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class MasterOfferingBase(BaseModel):
   title: str
   description: str
   price: Decimal
   duration_minutes: int


class MasterOfferingCreate(MasterOfferingBase):
    pass



class MasterOfferingUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    price: int | None = None
    duration_minutes: int | None = None

class MasterOfferingResponse(MasterOfferingBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    master_id: uuid.UUID
    is_active: bool