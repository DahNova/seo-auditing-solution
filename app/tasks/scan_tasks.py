from celery import current_app as celery_app
from datetime import datetime, timedelta
import logging

from app.core.celery_app import celery_app
from app.database import SyncSessionLocal
from app.models import Website, Scan, Schedule
from app.services.scan_service_sync import SyncScanService
from app.services.schedule_service import ScheduleService
from sqlalchemy import select
from sqlalchemy.orm import selectinload

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, max_retries=2)
def run_website_scan(self, website_id: int, scan_id: int = None):
    """Run SEO scan for a specific website using sync database operations"""
    try:
        # Use sync database operations to avoid async/sync conflicts
        with SyncSessionLocal() as db:
            # Get website first
            website = db.query(Website).filter(Website.id == website_id).first()
            
            if not website:
                raise ValueError(f"Website {website_id} not found")
            
            # Create or get scan
            if scan_id:
                scan = db.query(Scan).filter(Scan.id == scan_id).first()
                if not scan:
                    raise ValueError(f"Scan {scan_id} not found")
                scan_id_to_use = scan.id
            else:
                # Create new scan
                scan = Scan(website_id=website_id)
                db.add(scan)
                db.commit()
                db.refresh(scan)
                scan_id_to_use = scan.id
        
        # Run scan using sync service
        scan_service = SyncScanService()
        result = scan_service.run_scan(scan_id_to_use, website)
        
        logger.info(f"Scan completed successfully for website {website_id}")
        return {"status": "completed", "scan_id": scan_id_to_use, **result}
        
    except Exception as exc:
        logger.error(f"Scan failed for website {website_id}: {str(exc)}")
        
        # Retry with exponential backoff
        try:
            raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
        except self.MaxRetriesExceededError:
            logger.error(f"Max retries exceeded for website {website_id}")
            # Update scan status to failed using sync database
            try:
                with SyncSessionLocal() as db:
                    if scan_id:
                        scan = db.query(Scan).filter(Scan.id == scan_id).first()
                        if scan:
                            scan.status = "failed"
                            scan.error_message = str(exc)
                            scan.completed_at = datetime.utcnow()
                            db.commit()
            except Exception as db_error:
                logger.error(f"Failed to mark scan as failed in database: {str(db_error)}")
                
            return {"status": "failed", "error": str(exc)}

@celery_app.task
def run_scheduled_scans():
    """Run scheduled scans based on Schedule table using sync database"""
    try:
        with SyncSessionLocal() as db:
            # Get schedules that are due for execution
            now = datetime.utcnow()
            
            # Query schedules that are active and due for execution
            due_schedules = db.query(Schedule).options(
                selectinload(Schedule.website)
            ).filter(
                Schedule.is_active == True,
                Schedule.next_run_at <= now
            ).all()
            
            scheduled_count = 0
            for schedule in due_schedules:
                try:
                    # Ensure website exists and is active
                    if schedule.website and schedule.website.is_active:
                        logger.info(f"Scheduling scan for website {schedule.website.domain} (schedule ID: {schedule.id})")
                        
                        # Schedule the scan task
                        run_website_scan.delay(schedule.website.id)
                        scheduled_count += 1
                        
                        # Update schedule for next run
                        schedule.last_run_at = now
                        
                        # Calculate next run time based on frequency
                        frequency_hours = {
                            'daily': 24,
                            'weekly': 168,
                            'monthly': 720
                        }
                        
                        hours_to_add = frequency_hours.get(schedule.frequency, 720)
                        schedule.next_run_at = now + timedelta(hours=hours_to_add)
                        
                    else:
                        logger.warning(f"Schedule {schedule.id} has inactive/missing website, skipping")
                        
                except Exception as e:
                    logger.error(f"Error processing schedule {schedule.id}: {str(e)}")
                    # Mark schedule with error
                    schedule.last_run_at = now
                    schedule.last_error = str(e)
            
            # Commit all schedule updates
            db.commit()
            
            logger.info(f"✅ Scheduled {scheduled_count} scans from {len(due_schedules)} due schedules")
            return scheduled_count
            
    except Exception as e:
        logger.error(f"❌ Error in run_scheduled_scans: {str(e)}")
        return 0

def _needs_scan(website: Website, now: datetime) -> bool:
    """Check if website needs a scan based on frequency"""
    if not website.last_scan_at:
        return True
    
    frequency_hours = {
        'daily': 24,
        'weekly': 168,
        'monthly': 720
    }
    
    hours_since_last = frequency_hours.get(website.scan_frequency, 720)
    next_scan_time = website.last_scan_at + timedelta(hours=hours_since_last)
    
    return now >= next_scan_time