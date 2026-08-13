import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ReviewCreate(BaseModel):
    rating: int = Field(
        ge=1,
        le=5,
    )

    comment: str | None = Field(
        default=None,
        max_length=1000,
    )


class ReviewResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: uuid.UUID
    booking_id: uuid.UUID
    master_id: uuid.UUID
    client_id: uuid.UUID | None
    rating: int
    comment: str | None
    created_at: datetime


class ReviewStatsResponse(BaseModel):
    average_rating: float
    reviews_count: int