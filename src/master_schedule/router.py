import uuid

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
    status,
)

from src.master_schedule.dependencies import get_schedule_service
from src.master_schedule.schemas import (
    MasterScheduleCreate,
    MasterScheduleResponse,
    MasterScheduleUpdate,
)
from src.master_schedule.service import MasterScheduleService


router = APIRouter(tags=["Master schedules"])


@router.post(
    "/masters/{master_id}/schedules",
    response_model=MasterScheduleResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_schedule(
    master_id: uuid.UUID,
    data: MasterScheduleCreate,
    service: MasterScheduleService = Depends(
        get_schedule_service
    ),
):
    schedule = await service.create_schedule(
        master_id,
        data,
    )

    if schedule is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Расписание на этот день уже существует!",
        )

    return schedule


@router.get(
    "/masters/{master_id}/schedules",
    response_model=list[MasterScheduleResponse],
    status_code=status.HTTP_200_OK,
)
async def get_master_schedules(
    master_id: uuid.UUID,
    service: MasterScheduleService = Depends(
        get_schedule_service
    ),
):
    schedules = await service.get_master_schedules(
        master_id
    )

    return schedules


@router.get(
    "/schedules/{schedule_id}",
    response_model=MasterScheduleResponse,
    status_code=status.HTTP_200_OK,
)
async def get_schedule_by_id(
    schedule_id: uuid.UUID,
    service: MasterScheduleService = Depends(
        get_schedule_service
    ),
):
    schedule = await service.get_schedule_by_id(
        schedule_id
    )

    if schedule is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Расписание не найдено!",
        )

    return schedule


@router.patch(
    "/schedules/{schedule_id}",
    response_model=MasterScheduleResponse,
)
async def update_schedule(
    schedule_id: uuid.UUID,
    data: MasterScheduleUpdate,
    service: MasterScheduleService = Depends(
        get_schedule_service
    ),
):
    try:
        schedule = await service.update_schedule(
            schedule_id,
            data,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        )

    if schedule is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Расписание не найдено!",
        )

    return schedule


@router.delete(
    "/schedules/{schedule_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_schedule(
    schedule_id: uuid.UUID,
    service: MasterScheduleService = Depends(
        get_schedule_service
    ),
):
    deleted = await service.delete_schedule(
        schedule_id
    )

    if deleted is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Расписание не найдено!",
        )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )