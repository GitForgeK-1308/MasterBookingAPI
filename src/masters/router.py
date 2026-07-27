import uuid

from fastapi import HTTPException, status
from src.masters.schemas import MasterResponse
from src.masters.schemas import MasterCreate, MasterUpdate
from src.masters.service import MasterService
from src.masters.dependencies import get_master_service
from fastapi import APIRouter, status, Depends




router = APIRouter(prefix="/masters", tags=["Masters"])


@router.get(
    "/{master_id}",
    response_model=MasterResponse,
    status_code=status.HTTP_200_OK,
    
)

async def master_object(
    master_id: uuid.UUID,
    
    service: MasterService = Depends(get_master_service)
):
    query = await service.get_master_by_id(master_id)

    if not query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Мастер не найден!")

    return query
    



@router.get(
    "",
    response_model=list[MasterResponse],
    status_code=status.HTTP_200_OK
)

async def get_masters(
    service: MasterService = Depends(get_master_service)
):
    return await service.get_masters()




@router.post("", response_model=MasterResponse, status_code=201)
async def master_create(
    data: MasterCreate,
    service: MasterService = Depends(get_master_service)
):

    return await service.create_master(data)


@router.patch("/{master_id}", response_model=MasterResponse, status_code=200)
async def master_update(
    master_id: uuid.UUID,
    data: MasterUpdate,
    service: MasterService = Depends(get_master_service)
):

    master_update = await service.update_master(
        master_id,
        data
    )

    if not master_update:
        raise HTTPException(status_code=404, detail="Мастер не найден!")

    return master_update


@router.delete("/{master_id}", status_code=status.HTTP_204_NO_CONTENT)
async def master_delete(
    master_id: uuid.UUID,
    service: MasterService = Depends(get_master_service)
):

    master = await service.delete_master(master_id)

    if master is None:
        raise HTTPException(
            status_code=404,
            detail="Мастер не найден!"
        )
