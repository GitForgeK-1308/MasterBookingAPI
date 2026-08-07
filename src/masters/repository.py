import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.masters.models import Master


class MasterRepository:
    def __init__(self, session: AsyncSession):
        self.session = session



    async def get_all(self):
        result = await self.session.execute(
            select(Master)
        )

        return result.scalars().all()


    async def get_by_id(
        self,
        master_id: uuid.UUID
    ):

        return await self.session.scalar(
            select(Master).where(Master.id == master_id)
        )


    async def create(
        self,
        master: Master
    ):

        self.session.add(master)
        await self.session.commit()
        await self.session.refresh(master)

        return master

        
    async def update(
        self,
        master: Master
    ):

        await self.session.commit()
        await self.session.refresh(master)

        return master


    async def delete(self, master: Master):

        await self.session.delete(master)
        await self.session.commit()

        
       
    async def get_by_user_id(
    self,
    user_id: uuid.UUID,
    ) -> Master | None:
        return await self.session.scalar(
            select(Master).where(
                Master.user_id == user_id
            )
        )