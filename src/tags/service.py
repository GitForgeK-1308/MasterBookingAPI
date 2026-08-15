import uuid

from src.tags.exceptions import (
    TagAlreadyExistsError,
    TagNotFoundError,
)
from src.tags.models import Tag
from src.tags.repository import TagRepository
from src.tags.schemas import (
    TagCreate,
    TagUpdate,
)


class TagService:
    def __init__(
        self,
        repository: TagRepository,
    ):
        self.repository = repository
        

    async def get_tags(
        self,
    ) -> list[Tag]:
        return await self.repository.get_active()

    async def get_all_tags(
        self,
    ) -> list[Tag]:
        return await self.repository.get_all()

    async def create_tag(
        self,
        data: TagCreate,
    ) -> Tag:
        existing_by_name = await self.repository.get_by_name(
            data.name
        )

        if existing_by_name is not None:
            raise TagAlreadyExistsError

        slug = data.slug.lower()

        existing_by_slug = await self.repository.get_by_slug(
            slug
        )

        if existing_by_slug is not None:
            raise TagAlreadyExistsError

        tag = Tag(
            name=data.name,
            slug=slug,
        )

        return await self.repository.create(
            tag
        )

    async def update_tag(
    self,
    tag_id: uuid.UUID,
    data: TagUpdate,
) -> Tag:
        tag = await self.repository.get_by_id(
            tag_id
        )

        if tag is None:
            raise TagNotFoundError

        update_data = data.model_dump(
            exclude_unset=True
        )

        if "name" in update_data:
            existing_by_name = await self.repository.get_by_name(
                update_data["name"]
            )

            if (
                existing_by_name is not None
                and existing_by_name.id != tag.id
            ):
                raise TagAlreadyExistsError

        if "slug" in update_data:
            slug = update_data["slug"].lower()

            existing_by_slug = await self.repository.get_by_slug(
                slug
            )

            if (
                existing_by_slug is not None
                and existing_by_slug.id != tag.id
            ):
                raise TagAlreadyExistsError

            update_data["slug"] = slug

        for field, value in update_data.items():
            setattr(
                tag,
                field,
                value,
            )

        return await self.repository.update(
            tag
        )