import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.master_offering.models import MasterOffering
from src.master_offering.schemas import OfferingSort


class MasterOfferingRepository:
    def __init__(self, session: AsyncSession):
        self.session = session



    async def get_all(self):
        result = await self.session.execute(
            select(MasterOffering)
        )

        return result.scalars().all()


    async def get_by_id(
        self,
        offering_id: uuid.UUID
    ):

        return await self.session.scalar(
            select(MasterOffering).where(MasterOffering.id == offering_id)
        )


    async def create(
        self,
        offering: MasterOffering
    ):

        self.session.add(offering)
        await self.session.commit()
        await self.session.refresh(offering)

        return offering

        
    async def update(
        self,
        offering: MasterOffering
    ):

        await self.session.commit()
        await self.session.refresh(offering)

        return offering


    async def delete(self, offering: MasterOffering):

        await self.session.delete(offering)
        await self.session.commit()

        
       
    async def get_by_master_id(
    self,
    master_id: uuid.UUID,
) -> list[MasterOffering]:
        result = await self.session.scalars(
            select(MasterOffering)
            .where(
                MasterOffering.master_id == master_id
            )
            .order_by(MasterOffering.title)
        )

        return list(result.all())


    async def get_public_offerings(
    self,
    category_id: uuid.UUID | None = None,
    min_price: Decimal | None = None,
    max_price: Decimal | None = None,
    sort: OfferingSort | None = None,
) -> list[MasterOffering]:

        query = select(MasterOffering).where(
            MasterOffering.is_active.is_(True)
        )

        if category_id is not None:
            query = query.where(
                MasterOffering.category_id == category_id
            )

        if min_price is not None:
            query = query.where(
                MasterOffering.price >= min_price
            )

        if max_price is not None:
            query = query.where(
                MasterOffering.price <= max_price
            )

        if sort == OfferingSort.PRICE_ASC:
            query = query.order_by(
                MasterOffering.price.asc()
            )

        elif sort == OfferingSort.PRICE_DESC:
            query = query.order_by(
                MasterOffering.price.desc()
            )

        else:
            query = query.order_by(
                MasterOffering.title
            )

        result = await self.session.scalars(query)

        return list(result.all())