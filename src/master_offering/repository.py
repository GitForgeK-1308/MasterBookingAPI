import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.master_offering.models import MasterOffering


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

        
       
    