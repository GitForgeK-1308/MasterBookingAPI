import uuid

from src.categories.exceptions import (
    CategoryAlreadyExistsError,
    CategoryNotFoundError,
)
from src.categories.models import Category
from src.categories.repository import CategoryRepository
from src.categories.schemas import (
    CategoryCreate,
    CategoryUpdate,
)


class CategoryService:
    def __init__(
        self,
        repository: CategoryRepository,
    ):
        self.repository = repository

    async def get_categories(
        self,
    ) -> list[Category]:
        return await self.repository.get_active()

    async def get_all_categories(
        self,
    ) -> list[Category]:
        return await self.repository.get_all()

    async def get_category_by_id(
        self,
        category_id: uuid.UUID,
    ) -> Category:
        category = await self.repository.get_by_id(
            category_id
        )

        if category is None:
            raise CategoryNotFoundError

        return category

    async def create_category(
        self,
        data: CategoryCreate,
    ) -> Category:
        existing_by_name = await self.repository.get_by_name(
            data.name
        )

        if existing_by_name is not None:
            raise CategoryAlreadyExistsError

        existing_by_slug = await self.repository.get_by_slug(
            data.slug
        )

        if existing_by_slug is not None:
            raise CategoryAlreadyExistsError

        category = Category(
            name=data.name,
            slug=data.slug.lower(),
        )

        return await self.repository.create(
            category
        )

    async def update_category(
        self,
        category_id: uuid.UUID,
        data: CategoryUpdate,
    ) -> Category:
        category = await self.repository.get_by_id(
            category_id
        )

        if category is None:
            raise CategoryNotFoundError

        update_data = data.model_dump(
            exclude_unset=True
        )

        for field, value in update_data.items():
            setattr(
                category,
                field,
                value,
            )

        return await self.repository.update(
            category
        )