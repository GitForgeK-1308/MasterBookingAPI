import uuid
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field
from src.tags.schemas import TagResponse


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
    tag_ids: list[uuid.UUID] = Field(
    default_factory=list,
    max_length=10,
)

class MasterOfferingUpdate(BaseModel):
    category_id: uuid.UUID | None = None
    title: str | None = None
    description: str | None = None
    price: Decimal | None = None
    duration_minutes: int | None = None
    tag_ids: list[uuid.UUID] | None = Field(
    default=None,
    max_length=10,
)


class MasterOfferingResponse(MasterOfferingBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    category_id: uuid.UUID | None
    master_id: uuid.UUID
    tags: list[TagResponse] = Field(
    default_factory=list
)
    is_active: bool


class MasterOfferingPage(BaseModel):
    items: list[MasterOfferingResponse]
    total: int
    page: int
    page_size: int
    total_pages: int