import uuid
from io import BytesIO

from fastapi import UploadFile
from PIL import Image, UnidentifiedImageError

from src.master_offering.repository import MasterOfferingRepository
from src.offering_images.exceptions import (
    InvalidOfferingImageTypeError,
    OfferingImageAccessDeniedError,
    OfferingImageLimitExceededError,
    OfferingImageTooLargeError,
    OfferingNotFoundError
)
from src.offering_images.models import OfferingImage
from src.offering_images.repository import OfferingImageRepository
from src.offering_images.storage import LocalImageStorage


MAX_IMAGES_PER_OFFERING = 20

MAX_IMAGE_SIZE = 5 * 1024 * 1024


ALLOWED_IMAGE_FORMATS = {
    "JPEG": "jpg",
    "PNG": "png",
    "WEBP": "webp",
}


class OfferingImageService:
    def __init__(
        self,
        repository: OfferingImageRepository,
        offering_repository: MasterOfferingRepository,
        storage: LocalImageStorage,
    ):
        self.repository = repository
        self.offering_repository = offering_repository
        self.storage = storage


    def get_image_url(
        self,
        storage_key: str,
    ) -> str:
        return self.storage.get_url(storage_key)


    async def upload_image(
        self,
        offering_id: uuid.UUID,
        master_id: uuid.UUID,
        file: UploadFile,
    ) -> OfferingImage:

        offering = await self.offering_repository.get_by_id(
            offering_id
        )

        if offering is None:
            raise OfferingNotFoundError

        if offering.master_id != master_id:
            raise OfferingImageAccessDeniedError

        images_count = await self.repository.count_by_offering_id(
            offering_id
        )

        if images_count >= MAX_IMAGES_PER_OFFERING:
            raise OfferingImageLimitExceededError

        content = await file.read(
            MAX_IMAGE_SIZE + 1
        )

        if len(content) > MAX_IMAGE_SIZE:
            raise OfferingImageTooLargeError

        try:
            with Image.open(BytesIO(content)) as image:
                image_format = image.format

                image.verify()

        except (
            UnidentifiedImageError,
            OSError,
            Image.DecompressionBombError,
        ):
            raise InvalidOfferingImageTypeError

        if image_format not in ALLOWED_IMAGE_FORMATS:
            raise InvalidOfferingImageTypeError

        extension = ALLOWED_IMAGE_FORMATS[
            image_format
        ]

        storage_key = await self.storage.save(
            content=content,
            extension=extension,
        )

        image = OfferingImage(
            offering_id=offering_id,
            storage_key=storage_key,
            is_primary=images_count == 0,
            sort_order=images_count,
        )

        try:
            return await self.repository.create(
                image
            )

        except Exception:
            await self.storage.delete(
                storage_key
            )
            raise