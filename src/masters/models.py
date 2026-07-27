import uuid
from src.database.base import Base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column



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

    is_active: Mapped[bool] = mapped_column(default=False, nullable=False)