import uuid

from src.masters.exceptions import MasterProfileAlreadyExistsError
from src.masters.models import Master
from src.masters.repository import MasterRepository
from src.masters.schemas import MasterCreate, MasterProfileCreate, MasterUpdate
from src.users.repository import UserRepository
from src.users.models import User, UserRole

class MasterService:
    def __init__(
        self, 
        repository: MasterRepository,
        user_repository: UserRepository,
        ):

        self.repository = repository
        self.user_repository = user_repository



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

    
    async def create_master_profile(
    self,
    current_user: User,
    data: MasterProfileCreate,
) -> Master:
        existing_master = await self.repository.get_by_user_id(
            current_user.id
        )

        if existing_master is not None:
            raise MasterProfileAlreadyExistsError

        master = Master(
            user_id=current_user.id,
            first_name=current_user.first_name,
            last_name=current_user.last_name,
            description=data.description,
            experience=data.experience,
            education=data.education,
        )

        created_master = await self.repository.create(
            master
        )

        current_user.role = UserRole.MASTER

        await self.user_repository.update(
            current_user
        )

        return created_master