import uuid

from src.master_schedule.models import MasterSchedule
from src.master_schedule.repository import MasterScheduleRepository
from src.master_schedule.schemas import (
    MasterScheduleCreate,
    MasterScheduleUpdate,
)


class MasterScheduleService:
    def __init__(
        self,
        repository: MasterScheduleRepository,
    ):
        self.repository = repository

    async def get_schedule_by_id(
        self,
        schedule_id: uuid.UUID,
    ) -> MasterSchedule | None:
        schedule = await self.repository.get_by_id(
            schedule_id
        )

        if schedule is None:
            return None

        return schedule

    async def get_master_schedules(
        self,
        master_id: uuid.UUID,
    ) -> list[MasterSchedule]:
        schedules = await self.repository.get_by_master_id(
            master_id
        )

        return schedules

    async def create_schedule(
        self,
        master_id: uuid.UUID,
        data: MasterScheduleCreate,
    ) -> MasterSchedule | None:
        existing_schedule = (
            await self.repository.get_by_master_and_day(
                master_id=master_id,
                day_of_week=data.day_of_week,
            )
        )

        if existing_schedule is not None:
            return None

        new_schedule = MasterSchedule(
            master_id=master_id,
            day_of_week=data.day_of_week,
            start_time=data.start_time,
            end_time=data.end_time,
            is_working=data.is_working,
        )

        return await self.repository.create(
            new_schedule
        )


    async def update_schedule(
    self,
    schedule_id: uuid.UUID,
    data: MasterScheduleUpdate,
) -> MasterSchedule | None:

        schedule = await self.repository.get_by_id(schedule_id)

        if schedule is None:
            return None

        data_dict = data.model_dump(exclude_unset=True)

        new_start_time = data_dict.get(
            "start_time",
            schedule.start_time,
        )
        new_end_time = data_dict.get(
            "end_time",
            schedule.end_time,
        )
        new_is_working = data_dict.get(
            "is_working",
            schedule.is_working,
        )

        if new_is_working:
            if new_start_time is None or new_end_time is None:
                raise ValueError(
                    "Для рабочего дня необходимо указать время начала и окончания"
                )

            if new_start_time >= new_end_time:
                raise ValueError(
                    "Время начала должно быть раньше времени окончания"
                )

        else:
            new_start_time = None
            new_end_time = None

            data_dict["start_time"] = None
            data_dict["end_time"] = None

        for key, value in data_dict.items():
            setattr(schedule, key, value)

        return await self.repository.update(schedule)


    async def delete_schedule(
        self,
        schedule_id: uuid.UUID,
    ) -> bool | None:
        schedule = await self.repository.get_by_id(
            schedule_id
        )

        if schedule is None:
            return None

        await self.repository.delete(schedule)

        return True