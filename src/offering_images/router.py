import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from src.auth.dependencies import get_current_master_profile
from src.master_offering.exceptions import OfferingNotFoundError
from src.masters.models import Master
from src.offering_images.dependencies import get_offering_image_service
from src.offering_images.exceptions import (
    InvalidOfferingImageTypeError,
    OfferingImageAccessDeniedError,
    OfferingImageLimitExceededError,
    OfferingImageTooLargeError,
)
from src.offering_images.schemas import OfferingImageResponse
from src.offering_images.service import OfferingImageService


router = APIRouter(
    prefix="/offerings",
    tags=["Offering Images"],
)


@router.post(
    "/{offering_id}/images",
    response_model=OfferingImageResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_offering_image(
    offering_id: uuid.UUID,
    file: UploadFile = File(...),
    current_master: Master = Depends(
        get_current_master_profile
    ),
    service: OfferingImageService = Depends(
        get_offering_image_service
    ),
):
    try:
        image = await service.upload_image(
            offering_id=offering_id,
            master_id=current_master.id,
            file=file,
        )

        return OfferingImageResponse(
            id=image.id,
            offering_id=image.offering_id,
            image_url=service.get_image_url(
                image.storage_key
            ),
            is_primary=image.is_primary,
            sort_order=image.sort_order,
            created_at=image.created_at,
        )

    except OfferingNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Услуга не найдена!",
        )

    except OfferingImageAccessDeniedError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вы не можете загружать фотографии для чужой услуги!",
        )

    except OfferingImageLimitExceededError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Для одной услуги можно загрузить не более 20 фотографий!",
        )

    except OfferingImageTooLargeError:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Размер фотографии не должен превышать 5 MB!",
        )

    except InvalidOfferingImageTypeError:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Разрешены только JPEG, PNG и WEBP изображения!",
        )



@router.get(
    "/{offering_id}/images",
    response_model=list[OfferingImageResponse],
    status_code=status.HTTP_200_OK,
)
async def get_offering_images(
    offering_id: uuid.UUID,
    service: OfferingImageService = Depends(
        get_offering_image_service
    ),
):
    try:
        images = await service.get_offering_images(
            offering_id=offering_id
        )

        return [
            OfferingImageResponse(
                id=image.id,
                offering_id=image.offering_id,
                image_url=service.get_image_url(
                    image.storage_key
                ),
                is_primary=image.is_primary,
                sort_order=image.sort_order,
                created_at=image.created_at,
            )
            for image in images
        ]

    except OfferingNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Услуга не найдена!",
        )