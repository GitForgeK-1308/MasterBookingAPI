import uuid
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base

if TYPE_CHECKING:
    from src.masters.models import Master
    from src.bookings.models import Booking

class MasterOffering(Base):

    __tablename__ = "master_services"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    master_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(
            "masters.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )
        

    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    duration_minutes: Mapped[int] = mapped_column(
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)


    master: Mapped["Master"] = relationship(
        back_populates="master_services"
    )

    bookings: Mapped[list["Booking"]] = relationship(
        back_populates="offering",
    )