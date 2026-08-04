import uuid
from typing import TYPE_CHECKING

from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base

if TYPE_CHECKING:
    from src.master_offering.models import MasterOffering

class Master(Base):
    __tablename__ = "masters"


    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )


    first_name: Mapped[str] = mapped_column(String(20), nullable=False)
    last_name: Mapped[str] = mapped_column(String(25), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    experience: Mapped[int] = mapped_column(default=0, nullable=False)
    education: Mapped[str] = mapped_column(Text, nullable=False)

    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)



    master_services: Mapped[list["MasterOffering"]] = relationship(
        back_populates="master",
        cascade="all, delete-orphan",
        passive_deletes=True,
        )