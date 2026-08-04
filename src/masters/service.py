import uuid

from src.masters.models import Master
from src.masters.repository import MasterRepository
from src.masters.schemas import MasterCreate, MasterUpdate


class MasterService:
    def __init__(self, repository: MasterRepository):
        self.repository = repository



    async def get_master_by_id(
        self,
        master_id: uuid.UUID
    ):

        query = await self.repository.get_by_id(master_id)

        if not query:
            return None

        return query



    async def get_masters(self):
        db = await self.repository.get_all()

        return db


    async def create_master(self, data: MasterCreate):
        new_master = Master(
            first_name=data.first_name,
                last_name=data.last_name,
                description=data.description,
                experience=data.experience,
                education=data.education
        )

        return await self.repository.create(new_master)
    
    
    async def update_master(self, master_id: uuid.UUID, data: MasterUpdate):
        master = await self.repository.get_by_id(master_id)

        if not master:
            return None

        data_dict = data.model_dump(exclude_unset=True, exclude_none=True)

        for key, value in data_dict.items():
            setattr(master, key, value)

        update_master = await self.repository.update(master)

        return update_master

    
    async def delete_master(self, master_id: uuid.UUID):
        master = await self.repository.get_by_id(master_id)

        if master is None:
            return None

        await self.repository.delete(master)

        return True

    