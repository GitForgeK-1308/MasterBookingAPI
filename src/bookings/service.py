import uuid
from datetime import datetime, timedelta, date, time

from src.bookings.exceptions import (
    BookingAccessDeniedError,
    BookingInPastError,
    BookingNotFoundError,
    BookingOutsideWorkingHoursError,
    BookingTimeConflictError,
    ClientPhoneRequiredError,
    InvalidBookingStatusTransitionError,
    MasterInactiveError,
    MasterNotFoundError,
    MasterScheduleUnavailableError,
    OfferingDoesNotBelongToMasterError,
    OfferingInactiveError,
    OfferingNotFoundError,
)
from src.bookings.models import Booking, BookingStatus
from src.bookings.repository import BookingRepository
from src.bookings.schemas import (
    BookingCreate,
    BookingStatusUpdate,
    AvailableSlotsResponse
)
from src.master_offering.repository import (
    MasterOfferingRepository,
)
from src.master_schedule.models import WeekDay
from src.master_schedule.repository import (
    MasterScheduleRepository,
)
from src.masters.repository import MasterRepository
from src.users.models import User


WEEKDAY_BY_NUMBER = {
    0: WeekDay.MONDAY,
    1: WeekDay.TUESDAY,
    2: WeekDay.WEDNESDAY,
    3: WeekDay.THURSDAY,
    4: WeekDay.FRIDAY,
    5: WeekDay.SATURDAY,
    6: WeekDay.SUNDAY,
}

SLOT_STEP_MINUTES = 30

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
        current_user: User,
        data: BookingCreate,
    ) -> Booking:

        if current_user.phone is None:
            raise ClientPhoneRequiredError


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
            client_id=current_user.id,
            master_id=master_id,
            offering_id=data.offering_id,
            booking_date=data.booking_date,
            start_time=data.start_time,
            end_time=end_time,
            client_name=f"{current_user.first_name} {current_user.last_name}",
            client_phone=current_user.phone,
            client_email=current_user.email,
        )

        return await self.booking_repository.create(
            new_booking
        )

    async def update_booking_status(
    self,
    booking_id: uuid.UUID,
    master_id: uuid.UUID,
    data: BookingStatusUpdate,
) -> Booking:
        booking = await self.booking_repository.get_by_id(
            booking_id
        )

        if booking is None:
            raise BookingNotFoundError

        if booking.master_id != master_id:
            raise BookingAccessDeniedError

        allowed_transitions = {
            BookingStatus.PENDING: {
                BookingStatus.CONFIRMED,
            },
            BookingStatus.CONFIRMED: {
                BookingStatus.COMPLETED,
            },
        }

        allowed_statuses = allowed_transitions.get(
            booking.status,
            set(),
        )

        if data.status not in allowed_statuses:
            raise InvalidBookingStatusTransitionError

        booking.status = data.status

        return await self.booking_repository.update(
            booking
        )

        

    async def get_available_slots(
        self,
        master_id: uuid.UUID,
        offering_id: uuid.UUID,
        booking_date: date,
) -> AvailableSlotsResponse:

        master = await self.master_repository.get_by_id(
            master_id
        )

        if master is None:
            raise MasterNotFoundError

        if not master.is_active:
            raise MasterInactiveError

        offering = await self.offering_repository.get_by_id(
            offering_id
        )

        if offering is None:
            raise OfferingNotFoundError

        if not offering.is_active:
            raise OfferingInactiveError

        if offering.master_id != master_id:
            raise OfferingDoesNotBelongToMasterError

        if booking_date < date.today():
            raise BookingInPastError

        weekday_number = booking_date.weekday()

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


        existing_bookings = (
            await self.booking_repository.get_active_by_master_and_date(
                master_id=master_id,
                booking_date=booking_date,
            )
        )


        work_start = datetime.combine(
            booking_date,
            schedule.start_time,
        )

        work_end = datetime.combine(
            booking_date,
            schedule.end_time,
        )


        offering_duration = timedelta(
            minutes=offering.duration_minutes
        )


        slot_step = timedelta(
            minutes=SLOT_STEP_MINUTES
        )

        available_slots: list[time] = []

        current_start = work_start

        while current_start + offering_duration <= work_end:
            current_end = (
                current_start + offering_duration
            )

            if current_start > datetime.now():
                has_conflict = False

                for booking in existing_bookings:
                    existing_start = datetime.combine(
                        booking.booking_date,
                        booking.start_time,
                    )

                    existing_end = datetime.combine(
                        booking.booking_date,
                        booking.end_time,
                    )

                    if (
                        existing_start < current_end
                        and existing_end > current_start
                    ):
                        has_conflict = True
                        break

                if not has_conflict:
                    available_slots.append(
                        current_start.time()
                    )

            current_start += slot_step

        return AvailableSlotsResponse(
            master_id=master_id,
            offering_id=offering_id,
            booking_date=booking_date,
            slots=available_slots,
        )


    async def get_client_bookings(
    self,
    client_id: uuid.UUID,
    ) -> list[Booking]:
        return await self.booking_repository.get_by_client_id(
            client_id
        )

    
    async def cancel_client_booking(
    self,
    booking_id: uuid.UUID,
    client_id: uuid.UUID,
    ) -> Booking:
        booking = await self.booking_repository.get_by_id(
            booking_id
        )

        if booking is None:
            raise BookingNotFoundError

        if booking.client_id != client_id:
            raise BookingAccessDeniedError

        if booking.status not in {
            BookingStatus.PENDING,
            BookingStatus.CONFIRMED,
        }:
            raise InvalidBookingStatusTransitionError

        booking.status = BookingStatus.CANCELLED

        return await self.booking_repository.update(
            booking
        )


    