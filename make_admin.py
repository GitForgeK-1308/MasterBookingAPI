import asyncio

from sqlalchemy import select

from src.categories.models import Category
from src.master_offering.models import MasterOffering
from src.master_schedule.models import MasterSchedule
from src.masters.models import Master
from src.bookings.models import Booking
from src.database.session import AsyncSessionLocal
from src.users.models import User, UserRole


EMAIL = "admin@yahoo.com"


async def main():
    async with AsyncSessionLocal() as session:
        user = await session.scalar(
            select(User).where(
                User.email == EMAIL.lower()
            )
        )

        if user is None:
            print(f"Пользователь {EMAIL} не найден")
            return

        user.role = UserRole.ADMIN

        await session.commit()
        await session.refresh(user)

        print(
            f"Пользователь {user.email} теперь администратор"
        )


if __name__ == "__main__":
    asyncio.run(main())