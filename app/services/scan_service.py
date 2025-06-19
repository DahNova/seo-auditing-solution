import asyncio
from datetime import datetime
from typing import List, Dict, Any
import logging

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
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
                    cache_mode=CacheMode.BYPASS,
                    word_count_threshold=10,
                    screenshot=False,
                    check_robots_txt=website.robots_respect,
                    process_iframes=True,
                    excluded_tags=['script', 'style', 'nav', 'footer', 'aside']
                )
                
                # Start crawling
                async with AsyncWebCrawler(
                    config=browser_config,
                    verbose=True
                ) as crawler:
                    
                    # Use deep crawling with domain as-is (interface handles full URL)
                    try:
                        crawl_result = await strategy.arun(
                            start_url=website.domain,
                            crawler=crawler,
                            config=crawl_config
                        )
                    except Exception as crawl_error:
                        logger.warning(f"Deep crawling failed, attempting single page fallback: {str(crawl_error)}")
                        # Fallback to single page crawling if deep crawling fails
                        try:
                            crawl_result = await crawler.arun(
                                url=website.domain,
                                config=crawl_config
                            )
                            # Wrap single result in list to maintain compatibility
                            crawl_result = [crawl_result] if not hasattr(crawl_result, '__iter__') else crawl_result
                        except Exception as fallback_error:
                            logger.error(f"Both deep crawling and single page fallback failed: {str(fallback_error)}")
                            raise Exception(f"Crawling completely failed: {str(fallback_error)}")
                    
                    pages_scanned = 0
                    pages_failed = 0
                    total_issues = 0
                    
                    # Process each crawled page
                    # Handle both CrawlResultContainer and list-like results
                    logger.info(f"Crawl result type: {type(crawl_result)}, has results attr: {hasattr(crawl_result, 'results')}")
                    
                    if hasattr(crawl_result, 'results'):
                        # CrawlResultContainer case
                        results_to_process = crawl_result.results
                        logger.info(f"Using crawl_result.results, found {len(results_to_process)} results")
                    else:
                        # Direct list or other iterable case
                        results_to_process = crawl_result if hasattr(crawl_result, '__iter__') else [crawl_result]
                        logger.info(f"Using crawl_result directly, found {len(results_to_process)} results")
                    
                    for result in results_to_process:
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
                            
                            # Calculate SEO score for this page
                            page_score = self.seo_analyzer.scoring_engine.calculate_page_score(issues)
                            page.seo_score = page_score
                            page.issues_count = len(issues)
                            
                            total_issues += len(issues)
                            pages_scanned += 1
                            
                        except Exception as e:
                            # Log detailed error information
                            error_url = getattr(result, 'url', 'unknown_url')
                            error_status = getattr(result, 'status_code', 'unknown_status')
                            logger.error(f"Error processing page {error_url} (status: {error_status}): {str(e)}")
                            
                            # Still save failed page with minimal data for transparency
                            try:
                                failed_page = Page(
                                    scan_id=scan_id,
                                    url=error_url,
                                    status_code=error_status if error_status != 'unknown_status' else 500,
                                    response_time=getattr(result, 'response_time', None),
                                    title=f"Failed to process: {str(e)[:100]}",
                                    word_count=0,
                                    seo_score=0.0,
                                    issues_count=1
                                )
                                db.add(failed_page)
                                await db.flush()
                                
                                # Add error issue
                                error_issue = Issue(
                                    page_id=failed_page.id,
                                    issue_type="crawl_error",
                                    severity="high",
                                    message=f"Failed to crawl page: {str(e)}",
                                    recommendation="Check if the URL is accessible and the content format is supported"
                                )
                                db.add(error_issue)
                                total_issues += 1
                                
                            except Exception as save_error:
                                logger.error(f"Failed to save error information for {error_url}: {str(save_error)}")
                            
                            pages_failed += 1
                    
                    # Determine scan status based on success/failure ratio
                    total_pages = len(results_to_process)
                    success_ratio = pages_scanned / total_pages if total_pages > 0 else 0
                    
                    if pages_scanned == 0:
                        scan.status = "failed"
                        scan.error_message = "No pages could be processed successfully"
                    elif success_ratio >= 0.5:  # At least 50% success
                        scan.status = "completed"
                        if pages_failed > 0:
                            scan.error_message = f"{pages_failed} pages failed to process but scan completed"
                    else:
                        scan.status = "failed"
                        scan.error_message = f"Too many failures: {pages_failed}/{total_pages} pages failed"
                    
                    logger.info(f"Scan {scan_id}: {pages_scanned} succeeded, {pages_failed} failed, status: {scan.status}")
                    scan.completed_at = datetime.utcnow()
                    scan.pages_found = len(results_to_process)
                    scan.pages_scanned = pages_scanned
                    scan.pages_failed = pages_failed
                    scan.total_issues = total_issues
                    
                    # Calculate overall website SEO score
                    await db.flush()  # Ensure all pages are saved
                    page_scores = [p.seo_score for p in scan.pages if p.seo_score > 0]
                    if page_scores:
                        website_score_data = self.seo_analyzer.scoring_engine.calculate_website_score(page_scores)
                        scan.seo_score = website_score_data['average_score']
                    else:
                        scan.seo_score = 0.0
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
    
