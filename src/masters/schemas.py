import uuid
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class MasterBase(BaseModel):
    first_name: str = Field(min_length=1, max_length=20)
    last_name: str = Field(min_length=1, max_length=25)
    description: str = Field(min_length=1)
    experience: int = 0
    education: str = Field(min_length=1)

class MasterCreate(MasterBase):
    pass


FirstName = Annotated[str, Field(min_length=1, max_length=20)]
LastName = Annotated[str, Field(min_length=1, max_length=25)]
Description = Annotated[str, Field(min_length=1)]
Experience = Annotated[int, Field(ge=0)] 
Education = Annotated[str, Field(min_length=1)]


class MasterUpdate(BaseModel):
    first_name: FirstName | None = None
    last_name: LastName | None = None 
    description: Description | None = None 
    experience: Experience | None = None 
    education: Education | None = None

class MasterResponse(MasterBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    is_active: bool