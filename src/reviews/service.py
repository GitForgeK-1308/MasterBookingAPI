import uuid

from src.bookings.models import BookingStatus
from src.bookings.repository import BookingRepository
from src.reviews.exceptions import (
    BookingNotCompletedError,
    ReviewAccessDeniedError,
    ReviewAlreadyExistsError,
    ReviewBookingNotFoundError,
)
from src.reviews.models import Review
from src.reviews.repository import ReviewRepository
from src.reviews.schemas import ReviewCreate


class ReviewService:
    def __init__(
        self,
        repository: ReviewRepository,
        booking_repository: BookingRepository,
    ):
        self.repository = repository
        self.booking_repository = booking_repository

    async def create_review(
        self,
        booking_id: uuid.UUID,
        client_id: uuid.UUID,
        data: ReviewCreate,
    ) -> Review:
        booking = await self.booking_repository.get_by_id(
            booking_id
        )

        if booking is None:
            raise ReviewBookingNotFoundError

        if booking.client_id != client_id:
            raise ReviewAccessDeniedError

        if booking.status != BookingStatus.COMPLETED:
            raise BookingNotCompletedError

        existing_review = await self.repository.get_by_booking_id(
            booking_id
        )

        if existing_review is not None:
            raise ReviewAlreadyExistsError

        review = Review(
            booking_id=booking.id,
            master_id=booking.master_id,
            client_id=client_id,
            rating=data.rating,
            comment=data.comment,
        )

        return await self.repository.create(
            review
        )