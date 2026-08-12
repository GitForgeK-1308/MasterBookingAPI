import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.offering_images.models import OfferingImage


class OfferingImageRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(
        self,
        image_id: uuid.UUID,
    ) -> OfferingImage | None:
        return await self.session.scalar(
            select(OfferingImage).where(
                OfferingImage.id == image_id
            )
        )

    async def get_by_offering_id(
        self,
        offering_id: uuid.UUID,
    ) -> list[OfferingImage]:
        result = await self.session.scalars(
            select(OfferingImage)
            .where(
                OfferingImage.offering_id == offering_id
            )
            .order_by(
                OfferingImage.is_primary.desc(),
                OfferingImage.sort_order.asc(),
                OfferingImage.created_at.asc(),
            )
        )

        return list(result.all())

    async def count_by_offering_id(
        self,
        offering_id: uuid.UUID,
    ) -> int:
        count = await self.session.scalar(
            select(func.count(OfferingImage.id)).where(
                OfferingImage.offering_id == offering_id
            )
        )

        return count or 0

    async def get_primary(
        self,
        offering_id: uuid.UUID,
    ) -> OfferingImage | None:
        return await self.session.scalar(
            select(OfferingImage).where(
                OfferingImage.offering_id == offering_id,
                OfferingImage.is_primary.is_(True),
            )
        )

    async def create(
        self,
        image: OfferingImage,
    ) -> OfferingImage:
        self.session.add(image)

        await self.session.commit()
        await self.session.refresh(image)

        return image

    async def update(
        self,
        image: OfferingImage,
    ) -> OfferingImage:
        await self.session.commit()
        await self.session.refresh(image)

        return image

    async def delete(
        self,
        image: OfferingImage,
    ) -> None:
        await self.session.delete(image)
        await self.session.commit()