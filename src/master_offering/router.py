import uuid

from fastapi import APIRouter, Depends, HTTPException, status

from src.master_offering.dependencies import get_offering_service
from src.master_offering.schemas import (
    MasterOfferingCreate,
    MasterOfferingResponse,
    MasterOfferingUpdate,
)
from src.master_offering.service import MasterOfferingService

router = APIRouter(tags=["Offerings"])


@router.post(
    "/masters/{master_id}/offerings",
    response_model=MasterOfferingResponse,
    status_code=status.HTTP_201_CREATED,
    )

async def create_offering(
    master_id: uuid.UUID,
    data: MasterOfferingCreate, 
    service: MasterOfferingService = Depends(get_offering_service)
    ):
    
    offering = await service.create_offering(
        master_id,
        data,
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
    service: MasterOfferingService = Depends(get_offering_service)
):

    offering_update = await service.update_offering(
        offering_id,
        data,
    )


    if not offering_update:
        raise HTTPException(status_code=404, detail="Мастер не найден!")

    return offering_update


@router.delete(
    "/offerings/{offering_id}",
    status_code=status.HTTP_204_NO_CONTENT)
async def delete_offering(
    offering_id: uuid.UUID,
    service: MasterOfferingService = Depends(get_offering_service)
):

    master = await service.delete_offering(offering_id)

    if master is None:
        raise HTTPException(
            status_code=404,
            detail="Мастер не найден!"
        )




