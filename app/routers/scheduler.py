from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List
import asyncio
from datetime import datetime, timedelta

from app.database import get_db
from app.models import Website, Scan, Schedule
from app.core.celery_app import celery_app
from sqlalchemy import select, desc, func
from sqlalchemy.orm import selectinload

router = APIRouter(prefix="/api/v1/scheduler", tags=["scheduler"])

@router.get("/status")
async def get_scheduler_status() -> Dict[str, Any]:
    """Get overall scheduler status including worker and queue information"""
    try:
        # Get Celery inspector
        inspect = celery_app.control.inspect()
        
        # Get active workers
        active_workers = inspect.active()
        worker_count = len(active_workers) if active_workers else 0
        
        # Get queue length
        reserved_tasks = inspect.reserved()
        queue_length = sum(len(tasks) for tasks in reserved_tasks.values()) if reserved_tasks else 0
        
        # Get active tasks
        active_tasks = inspect.active()
        total_active = sum(len(tasks) for tasks in active_tasks.values()) if active_tasks else 0
        
        return {
            "worker_status": "online" if worker_count > 0 else "offline",
            "worker_count": worker_count,
            "queue_length": queue_length,
            "active_tasks": total_active,
            "last_updated": datetime.utcnow().isoformat()
        }
    except Exception as e:
        # Return error status if Celery is not available
        return {
            "worker_status": "error",
            "worker_count": 0,
            "queue_length": 0,
            "active_tasks": 0,
            "last_updated": datetime.utcnow().isoformat(),
            "error": f"Celery connection failed: {str(e)}"
        }

@router.get("/active-tasks")
async def get_active_tasks() -> List[Dict[str, Any]]:
    """Get currently running tasks"""
    try:
        inspect = celery_app.control.inspect()
        active_tasks = inspect.active()
        
        tasks = []
        if active_tasks:
            for worker, task_list in active_tasks.items():
                for task in task_list:
                    tasks.append({
                        "id": task.get("id"),
                        "name": task.get("name", "Unknown Task"),
                        "worker": worker,
                        "started_at": task.get("time_start"),
                        "args": task.get("args", []),
                        "kwargs": task.get("kwargs", {}),
                    })
        
        return tasks
    except Exception as e:
        # Return empty list if Celery is not available
        return []

@router.get("/recent-tasks")
async def get_recent_tasks(
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Get recently completed scans as a proxy for task history"""
    try:
        result = await db.execute(
            select(Scan, Website.domain)
            .join(Website)
            .order_by(desc(Scan.created_at))
            .limit(limit)
        )
        
        scans = result.all()
        
        recent_tasks = []
        for scan, domain in scans:
            task_name = f"Website Scan: {domain}"
            duration = None
            
            if scan.completed_at and scan.created_at:
                duration = int((scan.completed_at - scan.created_at).total_seconds())
            
            recent_tasks.append({
                "id": f"scan_{scan.id}",
                "task_name": task_name,
                "status": scan.status,
                "completed_at": scan.completed_at.isoformat() if scan.completed_at else None,
                "duration": duration,
                "error": scan.error_message if scan.status == "failed" else None
            })
        
        return recent_tasks
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching recent tasks: {str(e)}")

@router.get("/scheduled-scans")
async def get_scheduled_scans(db: AsyncSession = Depends(get_db)) -> List[Dict[str, Any]]:
    """Get all scheduled scans from Schedule table"""
    try:
        result = await db.execute(
            select(Schedule)
            .options(selectinload(Schedule.website))
            .where(Schedule.is_active == True)
            .order_by(Schedule.id)
        )
        
        schedules = result.scalars().all()
        
        scheduled_scans = []
        for schedule in schedules:
            if not schedule.website or not schedule.website.is_active:
                continue
                
            from datetime import timezone
            now = datetime.now(timezone.utc)
            is_overdue = schedule.next_run_at and schedule.next_run_at <= now
            
            scheduled_scans.append({
                "schedule_id": schedule.id,
                "website_id": schedule.website.id,
                "domain": schedule.website.domain,
                "name": schedule.website.name,
                "frequency": schedule.frequency,
                "last_run_at": schedule.last_run_at.isoformat() if schedule.last_run_at else None,
                "next_run_at": schedule.next_run_at.isoformat() if schedule.next_run_at else None,
                "is_overdue": is_overdue,
                "status": "overdue" if is_overdue else "scheduled",
                "error_count": schedule.error_count,
                "last_error": schedule.last_error
            })
        
        return scheduled_scans
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching scheduled scans: {str(e)}")

@router.get("/stats")
async def get_scheduler_stats(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """Get scheduler statistics using Schedule table"""
    try:
        today = datetime.utcnow().date()
        from datetime import timezone
        now = datetime.now(timezone.utc)
        
        # Scans completed today
        scans_today_result = await db.execute(
            select(func.count(Scan.id))
            .where(
                func.date(Scan.completed_at) == today,
                Scan.status == "completed"
            )
        )
        scans_today = scans_today_result.scalar() or 0
        
        # Failed scans today
        failed_today_result = await db.execute(
            select(func.count(Scan.id))
            .where(
                func.date(Scan.created_at) == today,
                Scan.status == "failed"
            )
        )
        failed_today = failed_today_result.scalar() or 0
        
        # Count total scheduled tasks (active schedules)
        total_scheduled_result = await db.execute(
            select(func.count(Schedule.id))
            .where(Schedule.is_active == True)
        )
        total_scheduled = total_scheduled_result.scalar() or 0
        
        # Count overdue schedules
        overdue_result = await db.execute(
            select(func.count(Schedule.id))
            .where(
                Schedule.is_active == True,
                Schedule.next_run_at <= now
            )
        )
        overdue_count = overdue_result.scalar() or 0
        
        # Find next scheduled scan
        next_schedule_result = await db.execute(
            select(Schedule)
            .options(selectinload(Schedule.website))
            .where(
                Schedule.is_active == True,
                Schedule.next_run_at > now
            )
            .order_by(Schedule.next_run_at)
            .limit(1)
        )
        next_schedule = next_schedule_result.scalar_one_or_none()
        
        next_scan_time = None
        next_scan_website = None
        if next_schedule and next_schedule.website:
            next_scan_time = next_schedule.next_run_at
            next_scan_website = next_schedule.website.domain
        
        # Get worker status for frontend compatibility
        inspect = celery_app.control.inspect()
        workers_online = 0
        queue_size = 0
        
        try:
            active_workers = inspect.active()
            workers_online = len(active_workers) if active_workers else 0
            
            reserved_tasks = inspect.reserved()
            queue_size = sum(len(tasks) for tasks in reserved_tasks.values()) if reserved_tasks else 0
        except Exception:
            # Set to 0 if Celery is not available
            workers_online = 0
            queue_size = 0
        
        return {
            # New Schedule-based metrics
            "scans_completed_today": scans_today,
            "scans_failed_today": failed_today,
            "overdue_count": overdue_count,
            "next_scan_time": next_scan_time.isoformat() if next_scan_time else None,
            "next_scan_website": next_scan_website,
            "generated_at": now.isoformat(),
            
            # Frontend-compatible properties
            "total_schedules": total_scheduled,
            "active_schedules": total_scheduled,  # Same as total for now
            "workers_online": workers_online,
            "queue_size": queue_size,
            "recent_tasks_count": scans_today  # Using scans completed today as proxy
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching scheduler stats: {str(e)}")

@router.post("/actions/purge-queue")
async def purge_queue() -> Dict[str, str]:
    """Purge all pending tasks from the queue"""
    try:
        celery_app.control.purge()
        return {"message": "Queue purged successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error purging queue: {str(e)}")

@router.post("/actions/pause")
async def pause_scheduler() -> Dict[str, str]:
    """Pause the scheduler (stop accepting new tasks)"""
    try:
        # Pause Celery workers by sending control command
        celery_app.control.cancel_consumer('celery')
        return {"message": "Scheduler paused - workers stopped accepting new tasks"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error pausing scheduler: {str(e)}")

@router.post("/actions/resume")
async def resume_scheduler() -> Dict[str, str]:
    """Resume the scheduler"""
    try:
        # Resume Celery workers by adding consumer back
        celery_app.control.add_consumer('celery')
        return {"message": "Scheduler resumed - workers accepting new tasks"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error resuming scheduler: {str(e)}")

@router.get("/worker-stats")
async def get_worker_stats() -> Dict[str, Any]:
    """Get detailed worker statistics"""
    try:
        inspect = celery_app.control.inspect()
        
        # Get worker stats
        stats = inspect.stats()
        active_workers = inspect.active()
        registered_tasks = inspect.registered()
        
        worker_details = []
        if stats:
            for worker_name, worker_stats in stats.items():
                active_tasks = len(active_workers.get(worker_name, [])) if active_workers else 0
                registered_task_count = len(registered_tasks.get(worker_name, [])) if registered_tasks else 0
                
                worker_details.append({
                    "name": worker_name,
                    "active_tasks": active_tasks,
                    "registered_tasks": registered_task_count,
                    "total_tasks": worker_stats.get("total", 0),
                    "pool_processes": worker_stats.get("pool", {}).get("processes", 0),
                    "broker": worker_stats.get("broker", {}),
                    "clock": worker_stats.get("clock", "Unknown")
                })
        
        return {
            "workers": worker_details,
            "total_workers": len(worker_details),
            "last_updated": datetime.utcnow().isoformat()
        }
    except Exception as e:
        # Return empty worker list if Celery is not available
        return {
            "workers": [],
            "total_workers": 0,
            "last_updated": datetime.utcnow().isoformat(),
            "error": f"Celery connection failed: {str(e)}"
        }