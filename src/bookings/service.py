import uuid
from datetime import datetime, timedelta

from src.bookings.exceptions import (
    BookingInPastError,
    BookingNotFoundError,
    BookingOutsideWorkingHoursError,
    BookingTimeConflictError,
    MasterInactiveError,
    MasterNotFoundError,
    MasterScheduleUnavailableError,
    OfferingDoesNotBelongToMasterError,
    OfferingInactiveError,
    OfferingNotFoundError,
)
from src.bookings.models import Booking
from src.bookings.repository import BookingRepository
from src.bookings.schemas import (
    BookingCreate,
    BookingStatusUpdate,
)
from src.master_offering.repository import (
    MasterOfferingRepository,
)
from src.master_schedule.models import WeekDay
from src.master_schedule.repository import (
    MasterScheduleRepository,
)
from src.masters.repository import MasterRepository


WEEKDAY_BY_NUMBER = {
    0: WeekDay.MONDAY,
    1: WeekDay.TUESDAY,
    2: WeekDay.WEDNESDAY,
    3: WeekDay.THURSDAY,
    4: WeekDay.FRIDAY,
    5: WeekDay.SATURDAY,
    6: WeekDay.SUNDAY,
}


class BookingService:
    def __init__(
        self,
        booking_repository: BookingRepository,
        master_repository: MasterRepository,
        offering_repository: MasterOfferingRepository,
        schedule_repository: MasterScheduleRepository,
    ):
        self.booking_repository = booking_repository
        self.master_repository = master_repository
        self.offering_repository = offering_repository
        self.schedule_repository = schedule_repository

    async def get_booking_by_id(
        self,
        booking_id: uuid.UUID,
    ) -> Booking:
        booking = await self.booking_repository.get_by_id(
            booking_id
        )

        if booking is None:
            raise BookingNotFoundError

        return booking

    async def get_master_bookings(
        self,
        master_id: uuid.UUID,
        booking_date,
    ) -> list[Booking]:
        master = await self.master_repository.get_by_id(
            master_id
        )

        if master is None:
            raise MasterNotFoundError

        return await self.booking_repository.get_by_master_and_date(
            master_id=master_id,
            booking_date=booking_date,
        )

    async def create_booking(
        self,
        master_id: uuid.UUID,
        data: BookingCreate,
    ) -> Booking:

        master = await self.master_repository.get_by_id(
            master_id
        )

        if master is None:
            raise MasterNotFoundError


        if not master.is_active:
            raise MasterInactiveError


        offering = await self.offering_repository.get_by_id(
            data.offering_id
        )

        if offering is None:
            raise OfferingNotFoundError


        if not offering.is_active:
            raise OfferingInactiveError


        if offering.master_id != master_id:
            raise OfferingDoesNotBelongToMasterError


        booking_start = datetime.combine(
            data.booking_date,
            data.start_time,
        )

        if booking_start <= datetime.now():
            raise BookingInPastError


        weekday_number = data.booking_date.weekday()

        day_of_week = WEEKDAY_BY_NUMBER[
            weekday_number
        ]

  
        schedule = (
            await self.schedule_repository.get_by_master_and_day(
                master_id=master_id,
                day_of_week=day_of_week,
            )
        )

        if schedule is None:
            raise MasterScheduleUnavailableError

        if not schedule.is_working:
            raise MasterScheduleUnavailableError

        if (
            schedule.start_time is None
            or schedule.end_time is None
        ):
            raise MasterScheduleUnavailableError

  
        booking_end = booking_start + timedelta(
            minutes=offering.duration_minutes
        )


        if booking_end.date() != data.booking_date:
            raise BookingOutsideWorkingHoursError

        end_time = booking_end.time()


        if data.start_time < schedule.start_time:
            raise BookingOutsideWorkingHoursError

        if end_time > schedule.end_time:
            raise BookingOutsideWorkingHoursError

 
        conflicting_booking = (
            await self.booking_repository.get_conflicting_booking(
                master_id=master_id,
                booking_date=data.booking_date,
                start_time=data.start_time,
                end_time=end_time,
            )
        )

        if conflicting_booking is not None:
            raise BookingTimeConflictError


        new_booking = Booking(
            master_id=master_id,
            offering_id=data.offering_id,
            booking_date=data.booking_date,
            start_time=data.start_time,
            end_time=end_time,
            client_name=data.client_name,
            client_phone=data.client_phone,
            client_email=data.client_email,
        )

        return await self.booking_repository.create(
            new_booking
        )

    async def update_booking_status(
        self,
        booking_id: uuid.UUID,
        data: BookingStatusUpdate,
    ) -> Booking:
        booking = await self.booking_repository.get_by_id(
            booking_id
        )

        if booking is None:
            raise BookingNotFoundError

        booking.status = data.status

        return await self.booking_repository.update(
            booking
        )