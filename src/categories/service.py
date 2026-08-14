import uuid

from src.categories.exceptions import (
    CategoryAlreadyExistsError,
    CategoryNotFoundError,
    CategoryInvalidParentError,
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

        slug = data.slug.lower()

        existing_by_slug = await self.repository.get_by_slug(
            slug
        )

        if existing_by_slug is not None:
            raise CategoryAlreadyExistsError

        if data.parent_id is not None:
            parent = await self.repository.get_by_id(
                data.parent_id
            )

            if parent is None:
                raise CategoryNotFoundError

        category = Category(
            name=data.name,
            slug=slug,
            parent_id=data.parent_id,
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

        if "parent_id" in update_data:
            parent_id = update_data["parent_id"]

        if parent_id == category.id:
            raise CategoryInvalidParentError

        if parent_id is not None:
            parent = await self.repository.get_by_id(
                parent_id
            )

            if parent is None:
                raise CategoryNotFoundError

            current_parent = parent

            while current_parent is not None:
                if current_parent.id == category.id:
                    raise CategoryInvalidParentError

                if current_parent.parent_id is None:
                    break

                current_parent = await self.repository.get_by_id(
                    current_parent.parent_id
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