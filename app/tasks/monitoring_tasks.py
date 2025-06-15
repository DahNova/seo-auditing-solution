from celery import current_app as celery_app
import hashlib
import logging
import asyncio
import httpx

from app.core.celery_app import celery_app
from app.database import AsyncSessionLocal
from app.models import Website, RobotsSnapshot, SitemapSnapshot
from sqlalchemy import select

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, max_retries=3)
def check_robots_sitemap(self, website_id: int):
    """Check robots.txt and sitemap for changes"""
    try:
        async def _check_changes():
            async with AsyncSessionLocal() as db:
                # Get website
                website_result = await db.execute(
                    select(Website).where(Website.id == website_id)
                )
                website = website_result.scalar_one_or_none()
                
                if not website:
                    raise ValueError(f"Website {website_id} not found")
                
                domain = website.domain
                changes_detected = False
                
                # Check robots.txt
                robots_changed = await _check_robots_txt(db, website, domain)
                if robots_changed:
                    changes_detected = True
                
                # Check sitemap
                sitemap_changed = await _check_sitemap(db, website, domain)
                if sitemap_changed:
                    changes_detected = True
                
                await db.commit()
                return changes_detected
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(_check_changes())
        loop.close()
        
        return {"status": "completed", "changes_detected": result}
        
    except Exception as exc:
        logger.error(f"Monitoring check failed for website {website_id}: {str(exc)}")
        
        try:
            raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
        except self.MaxRetriesExceededError:
            return {"status": "failed", "error": str(exc)}

@celery_app.task
def check_all_robots_sitemaps():
    """Check robots.txt and sitemaps for all active websites"""
    async def _check_all():
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(Website).where(Website.is_active == True)
            )
            websites = result.scalars().all()
            
            scheduled_count = 0
            for website in websites:
                # Schedule monitoring check for each website
                check_robots_sitemap.delay(website.id)
                scheduled_count += 1
            
            logger.info(f"Scheduled monitoring checks for {scheduled_count} websites")
            return scheduled_count
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(_check_all())
    loop.close()
    
    return result

async def _check_robots_txt(db, website: Website, domain: str) -> bool:
    """Check robots.txt for changes"""
    robots_url = f"https://{domain}/robots.txt"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(robots_url, timeout=10)
            
            content = response.text if response.status_code == 200 else ""
            content_hash = hashlib.md5(content.encode()).hexdigest()
            
            # Get last snapshot
            last_snapshot_result = await db.execute(
                select(RobotsSnapshot)
                .where(RobotsSnapshot.website_id == website.id)
                .order_by(RobotsSnapshot.created_at.desc())
                .limit(1)
            )
            last_snapshot = last_snapshot_result.scalar_one_or_none()
            
            has_changed = False
            if not last_snapshot or last_snapshot.content_hash != content_hash:
                has_changed = True
                
                # Create new snapshot
                new_snapshot = RobotsSnapshot(
                    website_id=website.id,
                    content_hash=content_hash,
                    content=content,
                    content_size=len(content),
                    is_accessible=response.status_code == 200,
                    status_code=response.status_code,
                    has_changed=has_changed,
                    previous_hash=last_snapshot.content_hash if last_snapshot else None
                )
                db.add(new_snapshot)
                
                if has_changed:
                    logger.info(f"Robots.txt changed for {domain}")
            
            return has_changed
            
    except Exception as e:
        logger.error(f"Error checking robots.txt for {domain}: {str(e)}")
        return False

async def _check_sitemap(db, website: Website, domain: str) -> bool:
    """Check sitemap for changes"""
    sitemap_urls = [
        f"https://{domain}/sitemap.xml",
        f"https://{domain}/sitemap_index.xml",
        f"https://{domain}/sitemaps.xml"
    ]
    
    for sitemap_url in sitemap_urls:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(sitemap_url, timeout=10)
                
                if response.status_code == 200:
                    content = response.text
                    content_hash = hashlib.md5(content.encode()).hexdigest()
                    
                    # Count URLs in sitemap (basic count)
                    urls_count = content.count('<url>') or content.count('<sitemap>')
                    
                    # Get last snapshot
                    last_snapshot_result = await db.execute(
                        select(SitemapSnapshot)
                        .where(
                            SitemapSnapshot.website_id == website.id,
                            SitemapSnapshot.sitemap_url == sitemap_url
                        )
                        .order_by(SitemapSnapshot.created_at.desc())
                        .limit(1)
                    )
                    last_snapshot = last_snapshot_result.scalar_one_or_none()
                    
                    has_changed = False
                    if not last_snapshot or last_snapshot.content_hash != content_hash:
                        has_changed = True
                        
                        # Create new snapshot
                        new_snapshot = SitemapSnapshot(
                            website_id=website.id,
                            sitemap_url=sitemap_url,
                            content_hash=content_hash,
                            urls_count=urls_count,
                            is_accessible=True,
                            status_code=response.status_code,
                            has_changed=has_changed,
                            previous_hash=last_snapshot.content_hash if last_snapshot else None,
                            previous_urls_count=last_snapshot.urls_count if last_snapshot else None
                        )
                        db.add(new_snapshot)
                        
                        if has_changed:
                            logger.info(f"Sitemap changed for {domain}: {sitemap_url}")
                    
                    return has_changed
                    
        except Exception as e:
            logger.error(f"Error checking sitemap {sitemap_url} for {domain}: {str(e)}")
            continue
    
    return False