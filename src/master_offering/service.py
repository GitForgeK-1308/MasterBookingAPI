from decimal import Decimal
import math
import uuid

from src.categories.exceptions import CategoryInactiveError, CategoryNotFoundError
from src.categories.repository import CategoryRepository
from src.master_offering.exceptions import OfferingAccessDeniedError, OfferingNotFoundError
from src.master_offering.models import MasterOffering
from src.master_offering.repository import MasterOfferingRepository
from src.master_offering.schemas import MasterOfferingCreate, MasterOfferingPage, MasterOfferingUpdate, OfferingSort


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
    
    
    async def update_offering(
    self,
    offering_id: uuid.UUID,
    master_id: uuid.UUID,
    data: MasterOfferingUpdate,
):
        offering = await self.repository.get_by_id(
            offering_id
        )

        if offering is None:
            return None

        if offering.master_id != master_id:
            raise OfferingAccessDeniedError

        data_dict = data.model_dump(
            exclude_unset=True,
            exclude_none=True,
        )

        if "category_id" in data_dict:
            category = await self.category_repository.get_by_id(
                data_dict["category_id"]
            )

            if category is None:
                raise CategoryNotFoundError

            if not category.is_active:
                raise CategoryInactiveError

        for key, value in data_dict.items():
            setattr(
                offering,
                key,
                value,
            )

        return await self.repository.update(
            offering
        )

    
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
    

    async def get_public_offerings(
    self,
    category_id: uuid.UUID | None = None,
    min_price: Decimal | None = None,
    max_price: Decimal | None = None,
    sort: OfferingSort | None = None,
    page: int = 1,
    page_size: int = 12,
) -> MasterOfferingPage:

        offset = (page - 1) * page_size

        offerings, total = await self.repository.get_public_offerings(
            category_id=category_id,
            min_price=min_price,
            max_price=max_price,
            sort=sort,
            offset=offset,
            limit=page_size,
        )

        total_pages = math.ceil(
            total / page_size
        ) if total > 0 else 0

        return MasterOfferingPage(
            items=offerings,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )