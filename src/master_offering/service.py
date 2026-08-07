import uuid

from src.master_offering.exceptions import OfferingAccessDeniedError
from src.master_offering.models import MasterOffering
from src.master_offering.repository import MasterOfferingRepository
from src.master_offering.schemas import MasterOfferingCreate, MasterOfferingUpdate


class MasterOfferingService:
    def __init__(self, repository: MasterOfferingRepository):
        self.repository = repository



    async def get_offering_by_id(
        self,
        offering_id: uuid.UUID
    ):

        query = await self.repository.get_by_id(offering_id)

        if not query:
            return None

        return query



    async def get_offerings(self):
        db = await self.repository.get_all()

        return db


    async def create_offering(self, master_id: uuid.UUID, data: MasterOfferingCreate):
        new_offering= MasterOffering(
                master_id=master_id,
                title=data.title,
                description=data.description,
                price=data.price,
                duration_minutes=data.duration_minutes,
        )

        return await self.repository.create(new_offering)
    
    
    async def update_offering(self, offering_id: uuid.UUID, master_id: uuid.UUID, data: MasterOfferingUpdate):
        offering = await self.repository.get_by_id(offering_id)

        if not offering:
            return None


        if offering.master_id != master_id:
            raise OfferingAccessDeniedError

        data_dict = data.model_dump(exclude_unset=True, exclude_none=True)

        for key, value in data_dict.items():
            setattr(offering, key, value)

        update_offering = await self.repository.update(offering)

        return update_offering

    
    async def delete_offering(self, offering_id: uuid.UUID, master_id: uuid.UUID):
        offering = await self.repository.get_by_id(offering_id)

        if offering is None:
            return None

        if offering.master_id != master_id:
            raise OfferingAccessDeniedError

        await self.repository.delete(offering)

        return True


    async def get_master_offerings(
    self,
    master_id: uuid.UUID,
    ) -> list[MasterOffering]:
        return await self.repository.get_by_master_id(
            master_id
        )
    