from celery import current_app as celery_app
from datetime import datetime, timedelta
import logging

from app.core.celery_app import celery_app
from app.database import AsyncSessionLocal
from app.models import Website, Scan
from app.services.scan_service import ScanService
from sqlalchemy import select

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, max_retries=3)
def run_website_scan(self, website_id: int, scan_id: int = None):
    """Run SEO scan for a specific website"""
    try:
        import asyncio
        import nest_asyncio
        
        # Allow nested event loops
        nest_asyncio.apply()
        
        async def _run_scan():
            async with AsyncSessionLocal() as db:
                try:
                    # Get website
                    website_result = await db.execute(
                        select(Website).where(Website.id == website_id)
                    )
                    website = website_result.scalar_one_or_none()
                    
                    if not website:
                        raise ValueError(f"Website {website_id} not found")
                    
                    # Create or get scan
                    if scan_id:
                        scan_result = await db.execute(
                            select(Scan).where(Scan.id == scan_id)
                        )
                        scan = scan_result.scalar_one_or_none()
                        if not scan:
                            raise ValueError(f"Scan {scan_id} not found")
                    else:
                        # Create new scan
                        scan = Scan(website_id=website_id)
                        db.add(scan)
                        await db.commit()
                        await db.refresh(scan)
                    
                    # Run scan
                    scan_service = ScanService()
                    await scan_service.run_scan(scan.id, website)
                    
                    return scan.id
                finally:
                    # Ensure proper cleanup
                    await db.close()
        
        # Try to get existing event loop, create new one if none exists
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                raise RuntimeError("Event loop is closed")
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # Run the async function
        result = loop.run_until_complete(_run_scan())
        
        logger.info(f"Scan completed successfully for website {website_id}")
        return {"status": "completed", "scan_id": result}
        
    except Exception as exc:
        logger.error(f"Scan failed for website {website_id}: {str(exc)}")
        
        # Retry with exponential backoff
        try:
            raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
        except self.MaxRetriesExceededError:
            logger.error(f"Max retries exceeded for website {website_id}")
            # Update scan status to failed
            try:
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                async def mark_failed():
                    async with AsyncSessionLocal() as db:
                        if scan_id:
                            scan_result = await db.execute(
                                select(Scan).where(Scan.id == scan_id)
                            )
                            scan = scan_result.scalar_one_or_none()
                            if scan:
                                scan.status = "failed"
                                scan.error_message = str(exc)
                                await db.commit()
                
                loop.run_until_complete(mark_failed())
                loop.close()
            except:
                pass
                
            return {"status": "failed", "error": str(exc)}

@celery_app.task
def run_scheduled_scans():
    """Run scheduled scans for all active websites"""
    import asyncio
    
    async def _run_scheduled():
        async with AsyncSessionLocal() as db:
            # Get websites that need scanning
            now = datetime.utcnow()
            
            # Query for websites that haven't been scanned recently
            result = await db.execute(
                select(Website).where(
                    Website.is_active == True,
                    # Add logic for frequency-based scheduling
                )
            )
            websites = result.scalars().all()
            
            scheduled_count = 0
            for website in websites:
                # Check if scan is needed based on frequency
                if _needs_scan(website, now):
                    # Schedule scan task
                    run_website_scan.delay(website.id)
                    scheduled_count += 1
            
            logger.info(f"Scheduled {scheduled_count} scans")
            return scheduled_count
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(_run_scheduled())
    loop.close()
    
    return result

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