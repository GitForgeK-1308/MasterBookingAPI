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
from src.reviews.schemas import MasterReviewResponse, ReviewCreate, ReviewStatsResponse, MasterReviewsResponse, ReviewPublicResponse


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


    async def get_master_reviews(
    self,
    master_id: uuid.UUID,
) -> list[Review]:
        return await self.repository.get_by_master_id(
            master_id
        )


    
    async def get_master_stats(
    self,
    master_id: uuid.UUID,
) -> ReviewStatsResponse:
        average_rating, reviews_count = (
            await self.repository.get_master_stats(
                master_id
            )
        )

        return ReviewStatsResponse(
            average_rating=average_rating,
            reviews_count=reviews_count,
        )


    async def get_master_reviews_with_stats(
    self,
    master_id: uuid.UUID,
) -> MasterReviewsResponse:
        rows = await self.repository.get_public_by_master_id(
            master_id
        )

        average_rating, reviews_count = (
            await self.repository.get_master_stats(
                master_id
            )
        )

        rating_distribution = (
            await self.repository.get_rating_distribution(
                master_id
            )
        )

        reviews = []

        for review, first_name, last_name in rows:
            if first_name is None:
                client_name = "Удалённый пользователь"
            else:
                client_name = f"{first_name} {last_name}"

            reviews.append(
                ReviewPublicResponse(
                    id=review.id,
                    rating=review.rating,
                    comment=review.comment,
                    client_name=client_name,
                    created_at=review.created_at,
                )
            )

        return MasterReviewsResponse(
            average_rating=average_rating,
            reviews_count=reviews_count,
            rating_distribution=rating_distribution,
            reviews=reviews,
        )


    async def get_reviews_for_master_dashboard(
    self,
    master_id: uuid.UUID,
) -> list[MasterReviewResponse]:
        rows = await self.repository.get_for_master_dashboard(
            master_id
        )

        reviews = []

        for (
            review,
            offering_id,
            offering_title,
            first_name,
            last_name,
        ) in rows:

            if first_name is None:
                client_name = "Удалённый пользователь"
            else:
                client_name = f"{first_name} {last_name}"

            reviews.append(
                MasterReviewResponse(
                    id=review.id,
                    offering_id=offering_id,
                    offering_title=offering_title,
                    rating=review.rating,
                    comment=review.comment,
                    client_name=client_name,
                    created_at=review.created_at,
                )
            )

        return reviews