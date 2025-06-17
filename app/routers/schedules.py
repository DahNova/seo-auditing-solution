from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database import get_db
from app.services.schedule_service import ScheduleService
from app.schemas.schedule import ScheduleCreate, ScheduleUpdate, ScheduleResponse
from app.tasks.scan_tasks import run_website_scan
from app.models.schedule import Schedule

router = APIRouter(prefix="/api/v1/schedules", tags=["schedules"])

@router.post("/", response_model=ScheduleResponse, status_code=status.HTTP_201_CREATED)
async def create_schedule(
    schedule_data: ScheduleCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new schedule for a website"""
    try:
        service = ScheduleService(db)
        schedule = await service.create_schedule(schedule_data)
        return schedule
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating schedule: {str(e)}")

@router.get("/", response_model=List[ScheduleResponse])
async def get_schedules(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get all schedules with pagination"""
    try:
        service = ScheduleService(db)
        schedules = await service.get_schedules(skip=skip, limit=limit)
        return schedules
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching schedules: {str(e)}")

@router.get("/{schedule_id}", response_model=ScheduleResponse)
async def get_schedule(
    schedule_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific schedule by ID"""
    try:
        service = ScheduleService(db)
        schedule = await service.get_schedule(schedule_id)
        if not schedule:
            raise HTTPException(status_code=404, detail="Schedule not found")
        return schedule
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching schedule: {str(e)}")

@router.put("/{schedule_id}", response_model=ScheduleResponse)
async def update_schedule(
    schedule_id: int,
    schedule_data: ScheduleUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update an existing schedule"""
    try:
        service = ScheduleService(db)
        schedule = await service.update_schedule(schedule_id, schedule_data)
        if not schedule:
            raise HTTPException(status_code=404, detail="Schedule not found")
        return schedule
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating schedule: {str(e)}")

@router.delete("/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_schedule(
    schedule_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a schedule"""
    try:
        service = ScheduleService(db)
        deleted = await service.delete_schedule(schedule_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Schedule not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting schedule: {str(e)}")

@router.post("/{schedule_id}/run-now")
async def run_schedule_now(
    schedule_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Execute a schedule immediately"""
    try:
        service = ScheduleService(db)
        schedule = await service.get_schedule(schedule_id)
        if not schedule:
            raise HTTPException(status_code=404, detail="Schedule not found")
        
        # Trigger the scan task
        task = run_website_scan.delay(schedule.website_id)
        
        return {
            "message": "Schedule executed successfully",
            "task_id": task.id,
            "website_id": schedule.website_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing schedule: {str(e)}")

@router.get("/due/list")
async def get_due_schedules(db: AsyncSession = Depends(get_db)):
    """Get schedules that are due for execution"""
    try:
        service = ScheduleService(db)
        due_schedules = await service.get_due_schedules()
        return {
            "count": len(due_schedules),
            "schedules": [
                {
                    "id": schedule.id,
                    "website_id": schedule.website_id,
                    "website_domain": schedule.website.domain if schedule.website else None,
                    "frequency": schedule.frequency,
                    "next_run_at": schedule.next_run_at
                }
                for schedule in due_schedules
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching due schedules: {str(e)}")

@router.post("/bulk/create")
async def create_bulk_schedules(
    frequency: str = "monthly",
    only_unscheduled: bool = True,
    db: AsyncSession = Depends(get_db)
):
    """Create schedules for all active websites"""
    try:
        from app.models.website import Website
        
        # Get all active websites
        websites_result = await db.execute(
            select(Website).where(Website.is_active == True)
        )
        websites = websites_result.scalars().all()
        
        if not websites:
            return {"message": "No active websites found", "created": 0, "skipped": 0}
        
        service = ScheduleService(db)
        created_count = 0
        skipped_count = 0
        
        for website in websites:
            try:
                # Check if schedule already exists if only_unscheduled is True
                if only_unscheduled:
                    existing_result = await db.execute(
                        select(Schedule).where(Schedule.website_id == website.id)
                    )
                    if existing_result.scalar_one_or_none():
                        skipped_count += 1
                        continue
                
                # Create schedule
                schedule_data = ScheduleCreate(
                    website_id=website.id,
                    frequency=frequency,
                    is_active=True
                )
                
                await service.create_schedule(schedule_data)
                created_count += 1
                
            except Exception as e:
                # Skip websites that fail (e.g., already have schedule)
                skipped_count += 1
                continue
        
        return {
            "message": f"Bulk scheduling completed",
            "created": created_count,
            "skipped": skipped_count,
            "total_websites": len(websites)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating bulk schedules: {str(e)}")