import uuid
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict


class OfferingSort(str, Enum):
    PRICE_ASC = "price_asc"
    PRICE_DESC = "price_desc"
    POPULAR = "popular"


class MasterOfferingBase(BaseModel):
    title: str
    description: str
    price: Decimal
    duration_minutes: int


class MasterOfferingCreate(MasterOfferingBase):
    category_id: uuid.UUID


class MasterOfferingUpdate(BaseModel):
    category_id: uuid.UUID | None = None
    title: str | None = None
    description: str | None = None
    price: Decimal | None = None
    duration_minutes: int | None = None


class MasterOfferingResponse(MasterOfferingBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    category_id: uuid.UUID | None
    master_id: uuid.UUID
    is_active: bool