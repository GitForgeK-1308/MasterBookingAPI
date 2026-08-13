import uuid

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.reviews.models import Review


class ReviewRepository:
    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session

    async def get_by_id(
        self,
        review_id: uuid.UUID,
    ) -> Review | None:
        return await self.session.scalar(
            select(Review).where(
                Review.id == review_id
            )
        )

    async def get_by_booking_id(
        self,
        booking_id: uuid.UUID,
    ) -> Review | None:
        return await self.session.scalar(
            select(Review).where(
                Review.booking_id == booking_id
            )
        )

    async def get_by_master_id(
        self,
        master_id: uuid.UUID,
    ) -> list[Review]:
        result = await self.session.scalars(
            select(Review)
            .where(
                Review.master_id == master_id
            )
            .order_by(
                Review.created_at.desc()
            )
        )

        return list(result.all())

    async def create(
        self,
        review: Review,
    ) -> Review:
        self.session.add(review)

        await self.session.commit()
        await self.session.refresh(review)

        return review


    async def get_master_stats(
    self,
    master_id: uuid.UUID,
) -> tuple[float, int]:
        result = await self.session.execute(
            select(
                func.avg(Review.rating),
                func.count(Review.id),
            ).where(
                Review.master_id == master_id
            )
        )

        average_rating, reviews_count = result.one()

        return (
            round(float(average_rating), 1)
            if average_rating is not None
            else 0.0,
            reviews_count,
        )