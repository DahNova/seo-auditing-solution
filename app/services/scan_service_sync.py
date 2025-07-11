"""
Synchronous ScanService for Celery tasks
Eliminates async/sync conflicts while maintaining crawling functionality
"""
import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import Website, Scan, Page, Issue
from app.database import SyncSessionLocal
from app.services.seo_analyzer.seo_analyzer import SEOAnalyzer
from app.services.url_utils import clean_url
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy

logger = logging.getLogger(__name__)


class SyncScanService:
    """Synchronous scan service for Celery background tasks"""
    
    def __init__(self):
        self.seo_analyzer = SEOAnalyzer()
    
    def run_scan(self, scan_id: int, website: Website) -> Dict[str, Any]:
        """
        Run complete SEO scan synchronously for Celery tasks
        Uses sync database but async crawling (which works fine)
        """
        try:
            with SyncSessionLocal() as db:
                # Get scan object
                scan = db.query(Scan).filter(Scan.id == scan_id).first()
                if not scan:
                    raise ValueError(f"Scan {scan_id} not found")
                
                # Update scan status
                scan.status = "running"
                scan.started_at = datetime.utcnow()
                db.commit()
                
                logger.info(f"Starting scan {scan_id} for website {website.domain}")
                
                # Run crawling (async part - works fine in new event loop)
                crawl_results = self._run_crawling_sync(website)
                
                # Process results with sync database
                return self._process_crawl_results_sync(db, scan, website, crawl_results)
                
        except Exception as e:
            logger.error(f"Scan {scan_id} failed: {str(e)}")
            # Update scan status to failed
            try:
                with SyncSessionLocal() as db:
                    scan = db.query(Scan).filter(Scan.id == scan_id).first()
                    if scan:
                        scan.status = "failed"
                        scan.error_message = str(e)
                        scan.completed_at = datetime.utcnow()
                        db.commit()
            except Exception as update_error:
                logger.error(f"Failed to update scan status: {update_error}")
            
            raise e
    
    def _run_crawling_sync(self, website: Website) -> List[Any]:
        """Run crawling in a clean event loop"""
        
        async def _crawl():
            browser_config = BrowserConfig(
                headless=True,
                verbose=False
            )
            
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
            
            async with AsyncWebCrawler(
                config=browser_config,
                verbose=True
            ) as crawler:
                
                try:
                    crawl_result = await strategy.arun(
                        start_url=website.domain,
                        crawler=crawler,
                        config=crawl_config
                    )
                except Exception as crawl_error:
                    logger.warning(f"Deep crawling failed, attempting single page fallback: {str(crawl_error)}")
                    # Fallback to single page crawling
                    try:
                        crawl_result = await crawler.arun(
                            url=website.domain,
                            config=crawl_config
                        )
                        # Convert single result to list for consistent processing
                        crawl_result = [crawl_result] if crawl_result else []
                    except Exception as fallback_error:
                        logger.error(f"Both deep crawling and fallback failed: {str(fallback_error)}")
                        raise fallback_error
                
                return crawl_result
        
        # Create clean event loop for crawling
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            results = loop.run_until_complete(_crawl())
            return results if isinstance(results, list) else [results] if results else []
        finally:
            loop.close()
            asyncio.set_event_loop(None)
    
    def _process_crawl_results_sync(self, db: Session, scan: Scan, website: Website, 
                                  crawl_results: List[Any]) -> Dict[str, Any]:
        """Process crawl results using sync database operations"""
        
        pages_scanned = 0
        pages_failed = 0
        pages_filtered = 0
        total_issues = 0
        
        # Convert results to list if single result
        results_to_process = crawl_results if isinstance(crawl_results, list) else [crawl_results]
        
        logger.info(f"Processing {len(results_to_process)} crawl results for scan {scan.id}")
        
        for result in results_to_process:
            if not result:
                pages_failed += 1
                continue
                
            try:
                # Extract basic page data
                url = getattr(result, 'url', '')
                if not url:
                    pages_failed += 1
                    continue
                
                # Clean URL to remove invisible characters
                url = clean_url(url)
                
                # Skip non-HTML content types - Don't save as pages but images should be analyzed within HTML pages
                non_html_extensions = [
                    # Images
                    '.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp', '.bmp', '.tiff', '.ico', 
                    # Documents
                    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
                    # Archives
                    '.zip', '.rar', '.tar', '.gz', '.7z',
                    # Executables
                    '.exe', '.dmg', '.pkg', '.deb', '.rpm',
                    # Fonts
                    '.woff', '.woff2', '.ttf', '.otf', '.eot',
                    # Data/Config
                    '.css', '.js', '.xml', '.json', '.txt', '.csv',
                    # Video/Audio
                    '.mp4', '.avi', '.mov', '.wmv', '.flv', '.mp3', '.wav', '.ogg'
                ]
                
                # Also check for URLs with query parameters that might be files
                url_lower = url.lower()
                is_non_html = any(url_lower.endswith(ext) for ext in non_html_extensions)
                
                # Additional check for URLs with query params pointing to files
                if not is_non_html and '?' in url:
                    # Check if query params suggest file download
                    if any(param in url_lower for param in ['file=', 'download=', 'attachment=']):
                        is_non_html = True
                
                if is_non_html:
                    logger.info(f"🔍 FILTERING OUT non-HTML content from pages: {url}")
                    pages_filtered += 1
                    continue
                
                # Create page record
                page = Page(
                    scan_id=scan.id,
                    url=url,
                    title=getattr(result, 'metadata', {}).get('title', '') if hasattr(result, 'metadata') else '',
                    meta_description=getattr(result, 'metadata', {}).get('description', '') if hasattr(result, 'metadata') else '',
                    status_code=getattr(result, 'status_code', 200),
                    word_count=len(getattr(result, 'markdown', '').split()) if hasattr(result, 'markdown') else 0
                )
                
                db.add(page)
                db.flush()  # Get page ID
                
                # Analyze page for SEO issues using async analyzer in sync context
                try:
                    # Run async analyzer in current thread (works fine)
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    try:
                        # Analyze page content for technical data
                        content_analysis = loop.run_until_complete(
                            self.seo_analyzer.analyze_page_content(result, url)
                        )
                        
                        # Extract technical SEO data
                        technical_data = content_analysis.get('technical_seo', {})
                        schema_data = technical_data.get('schema_markup', {})
                        mobile_data = technical_data.get('mobile_optimization', {})
                        
                        # NEW: Extract canonical URL and analyze URL structure
                        canonical_url = self.seo_analyzer.technical_seo_analyzer.extract_canonical_url(result)
                        url_analysis = self.seo_analyzer.technical_seo_analyzer.analyze_url_structure(url)
                        
                        # Update page with technical data
                        page.has_schema_markup = 1 if schema_data.get('has_schema', False) else 0
                        page.schema_types = schema_data.get('schema_types', [])
                        page.mobile_score = mobile_data.get('mobile_score', 0.0)
                        page.technical_score = technical_data.get('overall_score', 0.0)
                        page.technical_seo_data = technical_data
                        
                        # NEW: Set canonical and URL quality data
                        page.canonical_url = canonical_url
                        page.url_quality_score = url_analysis.get('url_quality_score', 100.0)
                        page.url_structure_data = url_analysis
                        
                        # Analyze issues
                        issues = loop.run_until_complete(
                            self.seo_analyzer.analyze_page_issues(result, page.id)
                        )
                        
                        # Create issue records
                        for issue_data in issues:
                            issue = Issue(page_id=page.id, **issue_data)
                            db.add(issue)
                        
                        # Calculate SEO score for this page
                        page_score = self.seo_analyzer.scoring_engine.calculate_page_score(issues)
                        page.seo_score = page_score
                        page.issues_count = len(issues)
                        
                        total_issues += len(issues)
                        pages_scanned += 1
                        
                    finally:
                        loop.close()
                        asyncio.set_event_loop(None)
                        
                except Exception as analysis_error:
                    logger.error(f"Error analyzing page {url}: {str(analysis_error)}")
                    
                    # Create error page anyway
                    page.seo_score = 0.0
                    page.issues_count = 0
                    
                    # Add error issue
                    error_issue = Issue(
                        page_id=page.id,
                        type="analysis_error",
                        category="technical",
                        severity="high",
                        title="Analysis Error",
                        description=f"Failed to analyze page: {str(analysis_error)}",
                        recommendation="Check if the page content is accessible and valid"
                    )
                    db.add(error_issue)
                    total_issues += 1
                    pages_failed += 1
                    
            except Exception as e:
                logger.error(f"Error processing crawl result for {getattr(result, 'url', 'unknown')}: {str(e)}")
                pages_failed += 1
                
                # Try to save failed page record
                try:
                    failed_page = Page(
                        scan_id=scan.id,
                        url=clean_url(getattr(result, 'url', 'unknown')),  # Clean URL to remove invisible characters
                        title='Failed to Process',
                        status_code=0,
                        word_count=0,
                        seo_score=0.0,
                        issues_count=1
                    )
                    db.add(failed_page)
                    db.flush()
                    
                    # Add error issue
                    error_issue = Issue(
                        page_id=failed_page.id,
                        type="crawl_error",
                        category="technical",
                        severity="high",
                        title="Crawl Error",
                        description=f"Failed to crawl page: {str(e)}",
                        recommendation="Check if the URL is accessible and the content format is supported"
                    )
                    db.add(error_issue)
                    total_issues += 1
                    
                except Exception as save_error:
                    logger.error(f"Failed to save error information: {str(save_error)}")
        
        # Finalize scan - calculate success based on HTML pages only (exclude filtered)
        total_pages = len(results_to_process)
        html_pages_attempted = total_pages - pages_filtered  # Exclude filtered files from calculation
        success_ratio = pages_scanned / html_pages_attempted if html_pages_attempted > 0 else 0
        
        if pages_scanned == 0:
            scan.status = "failed"
            scan.error_message = "No HTML pages could be processed successfully"
        elif success_ratio >= 0.5:  # At least 50% success of HTML pages
            scan.status = "completed"
            if pages_failed > 0:
                scan.error_message = f"{pages_failed} HTML pages failed to process but scan completed"
        else:
            scan.status = "failed"
            scan.error_message = f"Too many HTML page failures: {pages_failed}/{html_pages_attempted} pages failed"
        
        logger.info(f"Scan {scan.id}: {pages_scanned} succeeded, {pages_failed} failed, {pages_filtered} filtered, status: {scan.status}")
        scan.completed_at = datetime.utcnow()
        scan.pages_found = len(results_to_process)
        scan.pages_scanned = pages_scanned
        scan.pages_failed = pages_failed
        scan.total_issues = total_issues
        
        # NEW: Post-process for deduplication and canonical analysis
        try:
            self._post_process_duplicates_and_canonical(db, scan)
        except Exception as e:
            logger.warning(f"Error in duplicate/canonical post-processing: {str(e)}")
        
        # Calculate overall website SEO score
        db.flush()  # Ensure all pages are saved
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
        
        db.commit()
        logger.info(f"Scan {scan.id} completed successfully")
        
        return {
            "status": scan.status,
            "pages_scanned": pages_scanned,
            "pages_failed": pages_failed,
            "total_issues": total_issues,
            "seo_score": scan.seo_score
        }
    
    def _post_process_duplicates_and_canonical(self, db: Session, scan: Scan) -> None:
        """Post-process pages for duplicate detection and canonical analysis"""
        
        # Get all pages for this scan
        pages = db.query(Page).filter(Page.scan_id == scan.id).all()
        
        if not pages:
            return
        
        logger.info(f"🔍 Post-processing {len(pages)} pages for duplicate/canonical analysis")
        
        # Prepare data for duplicate analysis
        pages_data = []
        for page in pages:
            pages_data.append({
                'url': page.url,
                'canonical_url': page.canonical_url,
                'page_id': page.id
            })
        
        # Run duplicate content analysis
        duplicate_analysis = self.seo_analyzer.technical_seo_analyzer.detect_duplicate_content_issues(pages_data)
        
        # Group pages by canonical URL and set is_canonical flags
        canonical_groups = {}
        pages_without_canonical = []
        
        for page in pages:
            if page.canonical_url:
                canonical_url = page.canonical_url
                if canonical_url not in canonical_groups:
                    canonical_groups[canonical_url] = []
                canonical_groups[canonical_url].append(page)
            else:
                pages_without_canonical.append(page)
                # Pages without canonical are considered canonical themselves
                page.canonical_url = page.url
                page.is_canonical = 1
        
        # Process canonical groups
        group_counter = 0
        for canonical_url, group_pages in canonical_groups.items():
            group_counter += 1
            group_id = f"group_{scan.id}_{group_counter}"
            
            # Find the canonical page (the one that matches the canonical URL)
            canonical_page = None
            for page in group_pages:
                if page.url == canonical_url:
                    canonical_page = page
                    break
            
            # If no page matches canonical URL, pick the first one as canonical
            if not canonical_page and group_pages:
                canonical_page = group_pages[0]
                logger.warning(f"No page found for canonical URL {canonical_url}, using {canonical_page.url}")
            
            # Set flags for all pages in group
            for page in group_pages:
                page.duplicate_group_id = group_id
                page.is_canonical = 1 if page == canonical_page else 0
        
        # Create issues for duplicate content problems
        duplicate_issues = duplicate_analysis.get('duplicate_issues', [])
        for issue_data in duplicate_issues:
            # Create issue records for each affected page
            affected_pages = issue_data.get('affected_pages', [])
            for affected_url in affected_pages:
                # Find the page object
                affected_page = next((p for p in pages if p.url == affected_url), None)
                if affected_page:
                    duplicate_issue = Issue(
                        page_id=affected_page.id,
                        type=issue_data['type'],
                        category=issue_data['category'],
                        severity=issue_data['severity'],
                        title=issue_data['type'].replace('_', ' ').title(),
                        description=issue_data['message'],
                        recommendation=issue_data['recommendation']
                    )
                    db.add(duplicate_issue)
        
        # Create issues for URL structure problems
        for page in pages:
            url_issues = page.url_structure_data.get('url_issues', [])
            for url_issue_desc in url_issues:
                url_issue = Issue(
                    page_id=page.id,
                    type='url_structure_issue',
                    category='technical',
                    severity='medium',
                    title='URL Structure Issue',
                    description=url_issue_desc,
                    recommendation='Improve URL structure for better SEO'
                )
                db.add(url_issue)
        
        # Update scan statistics
        total_canonical_groups = len(canonical_groups)
        total_duplicates = sum(len(group) - 1 for group in canonical_groups.values() if len(group) > 1)
        
        logger.info(f"📊 Duplicate analysis complete:")
        logger.info(f"   Canonical groups: {total_canonical_groups}")
        logger.info(f"   Duplicate pages: {total_duplicates}")
        logger.info(f"   Pages without canonical: {len(pages_without_canonical)}")
        
        db.flush()  # Save all changes