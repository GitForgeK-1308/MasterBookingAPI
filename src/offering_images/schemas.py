import uuid
from datetime import datetime

from pydantic import BaseModel


class OfferingImageResponse(BaseModel):
    id: uuid.UUID
    offering_id: uuid.UUID
    image_url: str
    is_primary: bool
    sort_order: int
    created_at: datetime