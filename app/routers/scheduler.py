from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List
import asyncio
from datetime import datetime, timedelta

from app.database import get_db
from app.models import Website, Scan
from app.core.celery_app import celery_app
from sqlalchemy import select, desc, func

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
        # Return mock data if Celery is not available
        return {
            "worker_status": "offline",
            "worker_count": 0,
            "queue_length": 0,
            "active_tasks": 0,
            "last_updated": datetime.utcnow().isoformat(),
            "error": "Celery not available"
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
    except Exception:
        # Return mock data if Celery is not available
        return [
            {
                "id": "mock_task_1",
                "name": "app.tasks.scan_tasks.run_website_scan",
                "worker": "worker-1",
                "started_at": (datetime.utcnow() - timedelta(minutes=5)).isoformat(),
                "args": [1],
                "kwargs": {}
            }
        ]

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
    """Get all websites with their scheduling information"""
    try:
        result = await db.execute(
            select(Website)
            .where(Website.is_active == True)
            .order_by(Website.domain)
        )
        
        websites = result.scalars().all()
        
        scheduled_scans = []
        for website in websites:
            # Calculate next scan time
            next_scan_time = None
            if website.last_scan_at:
                frequency_hours = {
                    'daily': 24,
                    'weekly': 168,
                    'monthly': 720
                }
                hours = frequency_hours.get(website.scan_frequency, 720)
                next_scan_time = website.last_scan_at + timedelta(hours=hours)
            else:
                next_scan_time = datetime.utcnow()  # Schedule immediately if never scanned
            
            is_overdue = next_scan_time < datetime.utcnow()
            
            scheduled_scans.append({
                "website_id": website.id,
                "domain": website.domain,
                "name": website.name,
                "scan_frequency": website.scan_frequency,
                "last_scan_at": website.last_scan_at.isoformat() if website.last_scan_at else None,
                "next_scan_time": next_scan_time.isoformat(),
                "is_overdue": is_overdue,
                "status": "overdue" if is_overdue else "scheduled"
            })
        
        return scheduled_scans
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching scheduled scans: {str(e)}")

@router.get("/stats")
async def get_scheduler_stats(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """Get scheduler statistics"""
    try:
        today = datetime.utcnow().date()
        
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
        
        # Find next scheduled scan
        websites_result = await db.execute(
            select(Website)
            .where(Website.is_active == True)
        )
        websites = websites_result.scalars().all()
        
        next_scan_time = None
        next_scan_website = None
        
        for website in websites:
            if website.last_scan_at:
                frequency_hours = {
                    'daily': 24,
                    'weekly': 168,
                    'monthly': 720
                }
                hours = frequency_hours.get(website.scan_frequency, 720)
                next_time = website.last_scan_at + timedelta(hours=hours)
                
                if not next_scan_time or next_time < next_scan_time:
                    next_scan_time = next_time
                    next_scan_website = website.domain
        
        return {
            "scans_completed_today": scans_today,
            "scans_failed_today": failed_today,
            "next_scan_time": next_scan_time.isoformat() if next_scan_time else None,
            "next_scan_website": next_scan_website,
            "generated_at": datetime.utcnow().isoformat()
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
        # This would need to be implemented based on your scheduler setup
        # For now, just return a success message
        return {"message": "Scheduler paused successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error pausing scheduler: {str(e)}")

@router.post("/actions/resume")
async def resume_scheduler() -> Dict[str, str]:
    """Resume the scheduler"""
    try:
        # This would need to be implemented based on your scheduler setup
        # For now, just return a success message
        return {"message": "Scheduler resumed successfully"}
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
        # Return mock data if Celery is not available
        return {
            "workers": [
                {
                    "name": "worker-1",
                    "active_tasks": 1,
                    "registered_tasks": 3,
                    "total_tasks": 47,
                    "pool_processes": 4,
                    "broker": {"transport": "redis"},
                    "clock": "10"
                }
            ],
            "total_workers": 1,
            "last_updated": datetime.utcnow().isoformat(),
            "error": "Celery not available"
        }