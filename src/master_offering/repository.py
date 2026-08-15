import uuid
from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import and_, func, select, or_

from src.bookings.models import Booking, BookingStatus

from src.master_offering.models import MasterOffering
from src.master_offering.schemas import OfferingSort
from sqlalchemy.orm import selectinload

from src.tags.models import (
    Tag,
    master_offering_tags,
)

from src.categories.models import Category


class MasterOfferingRepository:
    def __init__(self, session: AsyncSession):
        self.session = session



    async def get_all(self):
        result = await self.session.execute(
            select(MasterOffering)
        )

        return result.scalars().all()


    async def get_by_id(
    self,
    offering_id: uuid.UUID,
):
        return await self.session.scalar(
            select(MasterOffering)
            .options(
                selectinload(
                    MasterOffering.tags
                )
            )
            .where(
                MasterOffering.id == offering_id
            )
        )


    async def create(
        self,
        offering: MasterOffering
    ):

        self.session.add(offering)
        await self.session.commit()
        await self.session.refresh(offering)

        return offering

        
    async def update(
        self,
        offering: MasterOffering
    ):

        await self.session.commit()
        await self.session.refresh(offering)

        return offering


    async def delete(self, offering: MasterOffering):

        await self.session.delete(offering)
        await self.session.commit()

        
       
    async def get_by_master_id(
    self,
    master_id: uuid.UUID,
) -> list[MasterOffering]:
        result = await self.session.scalars(
            select(MasterOffering)
            .where(
                MasterOffering.master_id == master_id
            )
            .order_by(MasterOffering.title)
        )

        return list(result.all())



    async def get_public_offerings(
    self,
    category_id: uuid.UUID | None = None,
    min_price: Decimal | None = None,
    max_price: Decimal | None = None,
    sort: OfferingSort | None = None,
    search: str | None = None,
    offset: int = 0,
    limit: int = 12,
) -> tuple[list[MasterOffering], int]:

        query = (
            select(MasterOffering)
            .options(
                selectinload(MasterOffering.tags)
            )
            .where(
                MasterOffering.is_active.is_(True)
            )
        )

        count_query = select(
            func.count(MasterOffering.id)
        ).where(
            MasterOffering.is_active.is_(True)
        )

        if category_id is not None:
            query = query.where(
                MasterOffering.category_id == category_id
            )

            count_query = count_query.where(
                MasterOffering.category_id == category_id
            )

        if min_price is not None:
            query = query.where(
                MasterOffering.price >= min_price
            )

            count_query = count_query.where(
                MasterOffering.price >= min_price
            )

        if max_price is not None:
            query = query.where(
                MasterOffering.price <= max_price
            )

            count_query = count_query.where(
                MasterOffering.price <= max_price
            )

        if search is not None:
            search = search.strip()

            if search:
                search_pattern = f"%{search}%"

                tag_match = (
                    select(1)
                    .select_from(
                        master_offering_tags.join(
                            Tag,
                            Tag.id == master_offering_tags.c.tag_id,
                        )
                    )
                    .where(
                        master_offering_tags.c.offering_id
                        == MasterOffering.id,
                        Tag.is_active.is_(True),
                        or_(
                            Tag.name.ilike(
                                search_pattern
                            ),
                            Tag.slug.ilike(
                                search_pattern
                            ),
                        ),
                    )
                    .exists()
                )

                category_match = (
                    select(1)
                    .select_from(Category)
                    .where(
                        Category.id == MasterOffering.category_id,
                        Category.is_active.is_(True),
                        or_(
                            Category.name.ilike(
                                search_pattern
                            ),
                            Category.slug.ilike(
                                search_pattern
                            ),
                        ),
                    )
                    .exists()
                )

                search_condition = or_(
                    MasterOffering.title.ilike(
                        search_pattern
                    ),
                    MasterOffering.description.ilike(
                        search_pattern
                    ),
                    tag_match,
                    category_match,
                )

                query = query.where(
                    search_condition
                )

                count_query = count_query.where(
                    search_condition
                )

        if sort == OfferingSort.PRICE_ASC:
            query = query.order_by(
                MasterOffering.price.asc()
            )

        elif sort == OfferingSort.PRICE_DESC:
            query = query.order_by(
                MasterOffering.price.desc()
            )

        elif sort == OfferingSort.POPULAR:
            query = (
                query
                .outerjoin(
                    Booking,
                    and_(
                        Booking.offering_id == MasterOffering.id,
                        Booking.status != BookingStatus.CANCELLED,
                    ),
                )
                .group_by(
                    MasterOffering.id
                )
                .order_by(
                    func.count(Booking.id).desc(),
                    MasterOffering.title.asc(),
                )
            )

        else:
            query = query.order_by(
                MasterOffering.title.asc()
            )

        total = await self.session.scalar(
            count_query
        )

        query = (
            query
            .offset(offset)
            .limit(limit)
        )

        result = await self.session.scalars(
            query
        )

        return list(result.all()), total or 0