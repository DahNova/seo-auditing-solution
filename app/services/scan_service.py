import asyncio
from datetime import datetime
from typing import List, Dict, Any
import logging

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models import Scan, Page, Issue, Website
from app.services.seo_analyzer import SEOAnalyzer

logger = logging.getLogger(__name__)

class ScanService:
    def __init__(self):
        self.seo_analyzer = SEOAnalyzer()
    
    async def run_scan(self, scan_id: int, website: Website):
        """Run a complete SEO scan for a website"""
        async with AsyncSessionLocal() as db:
            try:
                # Update scan status
                scan_result = await db.execute(
                    select(Scan).where(Scan.id == scan_id)
                )
                scan = scan_result.scalar_one()
                scan.status = "running"
                await db.commit()
                
                # Setup crawl4ai configuration
                browser_config = BrowserConfig(
                    headless=True,
                    browser_type="chromium"
                )
                
                # Deep crawling strategy with robots.txt respect
                strategy = BFSDeepCrawlStrategy(
                    max_depth=website.max_depth,
                    max_pages=website.max_pages,
                    include_external=website.include_external
                )
                
                crawl_config = CrawlerRunConfig(
                    respect_robots_txt=website.robots_respect,
                    cache_mode="bypass",
                    process_iframes=True,
                    extract_media=True,
                    word_count_threshold=10,
                    excluded_tags=['script', 'style', 'nav', 'footer', 'aside'],
                    screenshot=False
                )
                
                # Start crawling
                async with AsyncWebCrawler(
                    config=browser_config,
                    verbose=True
                ) as crawler:
                    
                    # Use deep crawling
                    crawl_result = await strategy.arun(
                        start_url=f"https://{website.domain}",
                        crawler=crawler,
                        config=crawl_config
                    )
                    
                    pages_scanned = 0
                    pages_failed = 0
                    total_issues = 0
                    
                    # Process each crawled page
                    for result in crawl_result.results:
                        try:
                            # Analyze page using Crawl4AI data directly
                            page_data = await self.seo_analyzer.analyze_page_content(result, website.domain)
                            
                            # Save page to database
                            page = Page(
                                scan_id=scan_id,
                                url=result.url,
                                status_code=result.status_code,
                                response_time=getattr(result, 'response_time', None),
                                **page_data
                            )
                            db.add(page)
                            await db.flush()
                            
                            # Save issues using Crawl4AI data
                            issues = await self.seo_analyzer.analyze_page_issues(result, page.id)
                            for issue_data in issues:
                                issue = Issue(page_id=page.id, **issue_data)
                                db.add(issue)
                            
                            total_issues += len(issues)
                            pages_scanned += 1
                            
                        except Exception as e:
                            logger.error(f"Error processing page {result.url}: {str(e)}")
                            pages_failed += 1
                    
                    # Update scan completion
                    scan.status = "completed"
                    scan.completed_at = datetime.utcnow()
                    scan.pages_found = len(crawl_result.results)
                    scan.pages_scanned = pages_scanned
                    scan.pages_failed = pages_failed
                    scan.total_issues = total_issues
                    scan.config = {
                        "max_depth": website.max_depth,
                        "max_pages": website.max_pages,
                        "robots_respect": website.robots_respect,
                        "include_external": website.include_external
                    }
                    
                    # Update website last scan time
                    website.last_scan_at = datetime.utcnow()
                    
                    await db.commit()
                    logger.info(f"Scan {scan_id} completed successfully")
                    
            except Exception as e:
                logger.error(f"Scan {scan_id} failed: {str(e)}")
                scan.status = "failed"
                scan.error_message = str(e)
                scan.completed_at = datetime.utcnow()
                await db.commit()
    
