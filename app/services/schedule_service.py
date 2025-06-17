from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload

from app.models.schedule import Schedule
from app.models.website import Website
from app.schemas.schedule import ScheduleCreate, ScheduleUpdate

class ScheduleService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_schedule(self, schedule_data: ScheduleCreate) -> Schedule:
        """Create a new schedule"""
        # Check if website exists
        website_result = await self.db.execute(
            select(Website).where(Website.id == schedule_data.website_id)
        )
        website = website_result.scalar_one_or_none()
        if not website:
            raise ValueError(f"Website {schedule_data.website_id} not found")

        # Check if schedule already exists for this website
        existing_result = await self.db.execute(
            select(Schedule).where(Schedule.website_id == schedule_data.website_id)
        )
        existing = existing_result.scalar_one_or_none()
        if existing:
            raise ValueError(f"Schedule already exists for website {schedule_data.website_id}")

        # Calculate next run time
        next_run_at = self._calculate_next_run(schedule_data.frequency)

        # Create schedule
        schedule = Schedule(
            website_id=schedule_data.website_id,
            frequency=schedule_data.frequency,
            is_active=schedule_data.is_active,
            next_run_at=next_run_at
        )
        
        self.db.add(schedule)
        await self.db.commit()
        await self.db.refresh(schedule)
        
        return schedule

    async def get_schedule(self, schedule_id: int) -> Optional[Schedule]:
        """Get schedule by ID"""
        result = await self.db.execute(
            select(Schedule)
            .options(selectinload(Schedule.website))
            .where(Schedule.id == schedule_id)
        )
        return result.scalar_one_or_none()

    async def get_schedules(self, skip: int = 0, limit: int = 100) -> List[Schedule]:
        """Get all schedules with pagination"""
        result = await self.db.execute(
            select(Schedule)
            .options(selectinload(Schedule.website))
            .offset(skip)
            .limit(limit)
            .order_by(Schedule.created_at.desc())
        )
        return result.scalars().all()

    async def update_schedule(self, schedule_id: int, schedule_data: ScheduleUpdate) -> Optional[Schedule]:
        """Update an existing schedule"""
        schedule = await self.get_schedule(schedule_id)
        if not schedule:
            return None

        # Update fields
        if schedule_data.frequency is not None:
            schedule.frequency = schedule_data.frequency
            # Recalculate next run if frequency changed
            schedule.next_run_at = self._calculate_next_run(schedule_data.frequency, schedule.last_run_at)

        if schedule_data.is_active is not None:
            schedule.is_active = schedule_data.is_active

        schedule.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(schedule)
        
        return schedule

    async def delete_schedule(self, schedule_id: int) -> bool:
        """Delete a schedule"""
        schedule = await self.get_schedule(schedule_id)
        if not schedule:
            return False

        await self.db.delete(schedule)
        await self.db.commit()
        
        return True

    async def get_due_schedules(self) -> List[Schedule]:
        """Get schedules that are due for execution"""
        now = datetime.utcnow()
        result = await self.db.execute(
            select(Schedule)
            .options(selectinload(Schedule.website))
            .where(
                and_(
                    Schedule.is_active == True,
                    Schedule.next_run_at <= now
                )
            )
        )
        return result.scalars().all()

    def _calculate_next_run(self, frequency: str, last_run: Optional[datetime] = None) -> datetime:
        """Calculate next run time based on frequency"""
        base_time = last_run or datetime.utcnow()
        
        frequency_deltas = {
            'hourly': timedelta(hours=1),
            'daily': timedelta(days=1),
            'weekly': timedelta(weeks=1),
            'monthly': timedelta(days=30)  # Approximate month
        }
        
        delta = frequency_deltas.get(frequency, timedelta(days=30))
        return base_time + delta

    async def mark_schedule_executed(self, schedule_id: int, error: Optional[str] = None):
        """Mark a schedule as executed and calculate next run"""
        schedule = await self.get_schedule(schedule_id)
        if not schedule:
            return

        now = datetime.utcnow()
        schedule.last_run_at = now
        schedule.next_run_at = self._calculate_next_run(schedule.frequency, now)
        
        if error:
            schedule.last_error = error
            schedule.error_count += 1
        else:
            schedule.last_error = None
            schedule.error_count = 0

        schedule.updated_at = now
        await self.db.commit()