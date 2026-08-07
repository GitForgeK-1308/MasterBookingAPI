import uuid

from src.categories.exceptions import CategoryInactiveError, CategoryNotFoundError
from src.categories.repository import CategoryRepository
from src.master_offering.exceptions import OfferingAccessDeniedError
from src.master_offering.models import MasterOffering
from src.master_offering.repository import MasterOfferingRepository
from src.master_offering.schemas import MasterOfferingCreate, MasterOfferingUpdate


class MasterOfferingService:
    def __init__(
        self, 
        repository: MasterOfferingRepository,
        category_repository: CategoryRepository,
        
        ):
        self.repository = repository
        self.category_repository = category_repository


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
        category = await self.category_repository.get_by_id(
        data.category_id
    )

        if category is None:
            raise CategoryNotFoundError

        if not category.is_active:
            raise CategoryInactiveError


        new_offering= MasterOffering(
                master_id=master_id,
                category_id=data.category_id,
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

        if "category_id" in data_dict:
            category = await self.category_repository.get_by_id(
                data_dict["category_id"]
            )

        if category is None:
            raise CategoryNotFoundError

        if not category.is_active:
            raise CategoryInactiveError

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
    