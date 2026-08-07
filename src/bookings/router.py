import uuid
from datetime import date

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from src.bookings.dependencies import get_booking_service
from src.bookings.exceptions import (
    BookingAccessDeniedError,
    BookingInPastError,
    BookingNotFoundError,
    BookingOutsideWorkingHoursError,
    BookingTimeConflictError,
    InvalidBookingStatusTransitionError,
    MasterInactiveError,
    MasterNotFoundError,
    MasterScheduleUnavailableError,
    OfferingDoesNotBelongToMasterError,
    OfferingInactiveError,
    OfferingNotFoundError,
)
from src.bookings.schemas import (
    BookingCreate,
    BookingResponse,
    BookingStatusUpdate,
    AvailableSlotsResponse
)
from src.bookings.service import BookingService

from src.auth.dependencies import get_current_client, get_current_master_profile, get_current_user
from src.masters.models import Master
from src.users.models import User
from src.bookings.exceptions import ClientPhoneRequiredError


router = APIRouter(tags=["Bookings"])


@router.post(
    "/masters/{master_id}/bookings",
    response_model=BookingResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_booking(
    master_id: uuid.UUID,
    data: BookingCreate,
    
    current_user: User = Depends(
        get_current_client
    ),
    service: BookingService = Depends(
        get_booking_service
    ),
):
    try:
        return await service.create_booking(
            master_id=master_id,
            current_user=current_user,
            data=data,
        )

    except ClientPhoneRequiredError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Для бронирования необходимо указать номер телефона!",
        )

    except MasterNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Мастер не найден!",
        )

    except MasterInactiveError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Мастер сейчас не принимает записи!",
        )

    except OfferingNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Услуга не найдена!",
        )

    except OfferingInactiveError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Услуга сейчас недоступна!",
        )

    except OfferingDoesNotBelongToMasterError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Услуга не принадлежит выбранному мастеру!",
        )

    except MasterScheduleUnavailableError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Мастер не работает в выбранный день!",
        )

    except BookingInPastError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Нельзя создать запись на прошедшее время!",
        )

    except BookingOutsideWorkingHoursError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Выбранное время находится вне рабочего времени мастера!",
        )

    except BookingTimeConflictError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Выбранное время уже занято!",
        )


@router.get(
    "/bookings/{booking_id}",
    response_model=BookingResponse,
    status_code=status.HTTP_200_OK,
)
async def get_booking_by_id(
    booking_id: uuid.UUID,
    service: BookingService = Depends(
        get_booking_service
    ),
):
    try:
        return await service.get_booking_by_id(
            booking_id
        )

    except BookingNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Бронирование не найдено!",
        )


@router.get(
    "/masters/{master_id}/bookings",
    response_model=list[BookingResponse],
    status_code=status.HTTP_200_OK,
)
async def get_master_bookings(
    master_id: uuid.UUID,
    booking_date: date,
    service: BookingService = Depends(
        get_booking_service
    ),
):
    try:
        return await service.get_master_bookings(
            master_id=master_id,
            booking_date=booking_date,
        )

    except MasterNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Мастер не найден!",
        )


@router.patch(
    "/bookings/{booking_id}/status",
    response_model=BookingResponse,
    status_code=status.HTTP_200_OK,
)
async def update_booking_status(
    booking_id: uuid.UUID,
    data: BookingStatusUpdate,
    service: BookingService = Depends(
        get_booking_service
    ),
):
    try:
        return await service.update_booking_status(
            booking_id=booking_id,
            data=data,
        )

    except BookingNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Бронирование не найдено!",
        )


@router.get(
    "/masters/{master_id}/available-slots",
    response_model=AvailableSlotsResponse,
    status_code=status.HTTP_200_OK,
)
async def get_available_slots(
    master_id: uuid.UUID,
    offering_id: uuid.UUID,
    booking_date: date,
    service: BookingService = Depends(
        get_booking_service
    ),
):
    try:
        return await service.get_available_slots(
            master_id=master_id,
            offering_id=offering_id,
            booking_date=booking_date,
        )

    except MasterNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Мастер не найден!",
        )

    except MasterInactiveError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Мастер сейчас не принимает записи!",
        )

    except OfferingNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Услуга не найдена!",
        )

    except OfferingInactiveError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Услуга сейчас недоступна!",
        )

    except OfferingDoesNotBelongToMasterError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Услуга не принадлежит выбранному мастеру!",
        )

    except MasterScheduleUnavailableError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Мастер не работает в выбранный день!",
        )

    except BookingInPastError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Нельзя получить слоты на прошедшую дату!",
        )


@router.get(
    "/users/me/bookings",
    response_model=list[BookingResponse],
)
async def get_my_bookings(
    current_user: User = Depends(
        get_current_user
    ),
    service: BookingService = Depends(
        get_booking_service
    ),
):
    return await service.get_client_bookings(
        client_id=current_user.id
    )


@router.get(
    "/masters/me/bookings",
    response_model=list[BookingResponse],
)
async def get_my_master_bookings(
    booking_date: date,
    current_master: Master = Depends(
        get_current_master_profile
    ),
    service: BookingService = Depends(
        get_booking_service
    ),
):
    return await service.get_master_bookings(
        master_id=current_master.id,
        booking_date=booking_date,
    )


@router.patch(
    "/users/me/bookings/{booking_id}/cancel",
    response_model=BookingResponse,
)
async def cancel_my_booking(
    booking_id: uuid.UUID,
    current_user: User = Depends(
        get_current_user
    ),
    service: BookingService = Depends(
        get_booking_service
    ),
):
    try:
        return await service.cancel_client_booking(
            booking_id=booking_id,
            client_id=current_user.id,
        )

    except BookingNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Бронирование не найдено!",
        )

    except BookingAccessDeniedError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вы не можете отменить чужое бронирование!",
        )

    except InvalidBookingStatusTransitionError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Это бронирование нельзя отменить!",
        )