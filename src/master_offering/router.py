import uuid

from fastapi import APIRouter, Depends, HTTPException, status

from src.master_offering.dependencies import get_offering_service
from src.master_offering.exceptions import OfferingAccessDeniedError
from src.master_offering.schemas import (
    MasterOfferingCreate,
    MasterOfferingResponse,
    MasterOfferingUpdate,
)
from src.master_offering.service import MasterOfferingService

from src.auth.dependencies import get_current_master_profile
from src.masters.models import Master

router = APIRouter(tags=["Offerings"])


@router.post(
    "/masters/me/offerings",
    response_model=MasterOfferingResponse,
    status_code=status.HTTP_201_CREATED,
    )

async def create_offering(
    data: MasterOfferingCreate, 
    current_master: Master = Depends(
        get_current_master_profile),
    service: MasterOfferingService = Depends(get_offering_service)
    ):
    
    offering = await service.create_offering(
        master_id=current_master.id,
        data=data
    )

    return offering



@router.get(
    "/offerings/{offering_id}",
    response_model=MasterOfferingResponse,
    status_code=status.HTTP_200_OK,
)


async def get_offering_by_id(
    offering_id: uuid.UUID, 
    service: MasterOfferingService = Depends(get_offering_service)
    ):
    
    offering = await service.get_offering_by_id(offering_id)

    if offering is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Услуга не найдена!")

    return offering


@router.patch(
    "/offerings/{offering_id}",
    response_model=MasterOfferingResponse,
)


async def patch_offering(
    data: MasterOfferingUpdate,
    offering_id: uuid.UUID, 
    current_master: Master = Depends(
        get_current_master_profile),
    service: MasterOfferingService = Depends(get_offering_service)
):

    try:
        offering_update = await service.update_offering(
            offering_id,
            data,
        )


        if not offering_update:
            raise HTTPException(status_code=404, detail="Услуга не найдена!")

        return offering_update

    except OfferingAccessDeniedError:
         raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вы не можете изменять чужую услугу!",
        )


@router.delete(
    "/offerings/{offering_id}",
    status_code=status.HTTP_204_NO_CONTENT)

async def delete_offering(
    offering_id: uuid.UUID,
    service: MasterOfferingService = Depends(get_offering_service)
):
    try: 
        delete_offering = await service.delete_offering(offering_id)

        if delete_offering is None:
            raise HTTPException(
                status_code=404,
                detail="Услуга не найдена!"
            )

    except OfferingAccessDeniedError:
         raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вы не можете удалять чужую услугу!",
        ) 



