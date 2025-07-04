"""
Enterprise Scan Service with Sitemap-Based URL Discovery
Advanced SEO scanning with multi-source URL discovery, priority-based crawling,
and comprehensive sitemap integration for enterprise-scale auditing.
"""
import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import Website, Scan, Page, Issue, SitemapSnapshot, RobotsSnapshot
from app.database import SyncSessionLocal
from app.services.seo_analyzer.seo_analyzer import SEOAnalyzer
from app.services.url_utils import clean_url, normalize_url
from app.services.sitemap_parser import SitemapParser
from app.services.url_discovery_service import URLDiscoveryService, URLDiscoveryConfig, DiscoveredURL, URLSource
from app.services.url_queue_manager import URLQueueManager, CrawlBudget, QueuedURL

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
import hashlib

logger = logging.getLogger(__name__)

class EnterpriseScanService:
    """Enterprise scan service with sitemap-based URL discovery"""
    
    def __init__(self):
        self.seo_analyzer = SEOAnalyzer()
        self.discovery_config = URLDiscoveryConfig()
        
    def run_enterprise_scan(self, scan_id: int, website: Website) -> Dict[str, Any]:
        """
        Run enterprise SEO scan with sitemap-first URL discovery
        Phase 1: URL Discovery (Sitemaps + Crawling + Manual)
        Phase 2: Priority-Based Processing
        Phase 3: SEO Analysis
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
                
                logger.info(f"Starting enterprise scan {scan_id} for website {website.domain}")
                
                # Phase 1: Multi-Source URL Discovery
                discovery_results = self._run_url_discovery_sync(website, db)
                
                # Phase 2: Priority-Based URL Processing
                processing_results = self._process_urls_with_priority_sync(
                    db, scan, website, discovery_results
                )
                
                # Update scan completion
                scan.status = "completed"
                scan.completed_at = datetime.utcnow()
                db.commit()
                
                # Combine results - filter out non-serializable objects
                serializable_discovery_results = {
                    'domain': discovery_results.get('domain'),
                    'total_urls': discovery_results.get('total_urls', 0),
                    'sources': {
                        'sitemap': {'count': discovery_results.get('sources', {}).get('sitemap', {}).get('count', 0)},
                        'crawl': {'count': discovery_results.get('sources', {}).get('crawl', {}).get('count', 0)},
                        'manual': {'count': discovery_results.get('sources', {}).get('manual', {}).get('count', 0)}
                    },
                    'statistics': discovery_results.get('statistics', {})
                }
                
                final_results = {
                    **serializable_discovery_results,
                    **processing_results,
                    'scan_type': 'enterprise',
                    'total_time': (scan.completed_at - scan.started_at).total_seconds()
                }
                
                logger.info(f"Enterprise scan {scan_id} completed successfully")
                return final_results
                
        except Exception as e:
            logger.error(f"Enterprise scan {scan_id} failed: {str(e)}")
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
    
    def _run_url_discovery_sync(self, website: Website, db: Session) -> Dict[str, Any]:
        """Run comprehensive URL discovery in sync context"""
        
        async def _discover_urls():
            """Async URL discovery function"""
            # Get robots.txt content for sitemap discovery
            robots_content = self._get_robots_content(website, db)
            
            # Configure URL discovery based on website settings
            config = URLDiscoveryConfig()
            config.max_crawl_pages = website.max_pages
            config.max_crawl_depth = website.max_depth
            config.crawl_external = website.include_external
            
            # Create discovery service
            discovery_service = URLDiscoveryService(config)
            
            # Run discovery
            discovery_results = await discovery_service.discover_urls(
                domain=website.domain,
                robots_content=robots_content,
                manual_urls=self._get_manual_urls(website),
                crawl_config={
                    'max_depth': website.max_depth,
                    'max_pages': website.max_pages,
                    'include_external': website.include_external
                }
            )
            
            return discovery_results
        
        # Run in clean event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            results = loop.run_until_complete(_discover_urls())
            
            # Store sitemap snapshots for monitoring
            self._store_sitemap_snapshots(website, results, db)
            
            return results
        finally:
            loop.close()
            asyncio.set_event_loop(None)
    
    def _get_robots_content(self, website: Website, db: Session) -> Optional[str]:
        """Get latest robots.txt content from database"""
        robots_snapshot = db.query(RobotsSnapshot)\
            .filter(RobotsSnapshot.website_id == website.id)\
            .order_by(RobotsSnapshot.created_at.desc())\
            .first()
        
        return robots_snapshot.content if robots_snapshot and robots_snapshot.is_accessible else None
    
    def _get_manual_urls(self, website: Website) -> List[str]:
        """Get manually configured URLs for the website"""
        # This could be extended to support custom URL lists
        # For now, return empty list
        return []
    
    def _store_sitemap_snapshots(self, website: Website, discovery_results: Dict[str, Any], db: Session):
        """Store sitemap snapshots for monitoring and change detection"""
        sitemap_sources = discovery_results.get('sources', {}).get('sitemap', {})
        sitemap_urls = sitemap_sources.get('urls', [])
        
        for sitemap_url in sitemap_urls:
            if hasattr(sitemap_url, 'source_sitemap') and sitemap_url.source_sitemap:
                # Create or update sitemap snapshot
                existing_snapshot = db.query(SitemapSnapshot)\
                    .filter(
                        SitemapSnapshot.website_id == website.id,
                        SitemapSnapshot.sitemap_url == sitemap_url.source_sitemap
                    ).first()
                
                # Calculate content hash for change detection
                content_hash = hashlib.md5(str(sitemap_url.source_sitemap).encode()).hexdigest()
                
                if existing_snapshot:
                    existing_snapshot.urls_count = 1  # Update with actual count
                    existing_snapshot.content_hash = content_hash
                    existing_snapshot.is_accessible = True
                else:
                    new_snapshot = SitemapSnapshot(
                        website_id=website.id,
                        sitemap_url=sitemap_url.source_sitemap,
                        content_hash=content_hash,
                        urls_count=1,
                        is_accessible=True,
                        sitemap_type='regular'
                    )
                    db.add(new_snapshot)
        
        db.commit()
    
    def _process_urls_with_priority_sync(
        self, 
        db: Session, 
        scan: Scan, 
        website: Website, 
        discovery_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process discovered URLs using priority-based queue management"""
        
        discovered_urls = discovery_results.get('urls', [])
        
        if not discovered_urls:
            logger.warning(f"No URLs discovered for website {website.domain}")
            return {
                'pages_scanned': 0,
                'pages_failed': 0,
                'total_issues': 0,
                'processing_method': 'priority_queue'
            }
        
        # Create crawl budget based on website settings
        crawl_budget = CrawlBudget(
            total_budget=website.max_pages,
            time_budget=3600  # 1 hour default
        )
        
        # Initialize queue manager
        queue_manager = URLQueueManager(crawl_budget)
        
        # Add discovered URLs to queue
        queue_manager.add_urls(discovered_urls)
        
        logger.info(f"Added {len(discovered_urls)} URLs to priority queue for scan {scan.id}")
        
        # Process URLs in priority order
        return self._process_priority_queue_sync(db, scan, website, queue_manager)
    
    def _process_priority_queue_sync(
        self, 
        db: Session, 
        scan: Scan, 
        website: Website, 
        queue_manager: URLQueueManager
    ) -> Dict[str, Any]:
        """Process URLs from priority queue using batch processing"""
        
        pages_scanned = 0
        pages_failed = 0
        total_issues = 0
        batch_size = 5  # Process 5 URLs at a time
        
        async def _process_batch(batch: List[QueuedURL]):
            """Process a batch of URLs asynchronously"""
            browser_config = BrowserConfig(headless=True, verbose=False)
            crawl_config = CrawlerRunConfig(
                cache_mode=CacheMode.BYPASS,
                word_count_threshold=10,
                screenshot=False,
                check_robots_txt=website.robots_respect,
                process_iframes=True,
                excluded_tags=['script', 'style', 'nav', 'footer', 'aside']
            )
            
            async with AsyncWebCrawler(config=browser_config, verbose=False) as crawler:
                batch_results = []
                
                for queued_url in batch:
                    try:
                        # Crawl the URL
                        result = await crawler.arun(
                            url=queued_url.url,
                            config=crawl_config
                        )
                        
                        if result and result.success:
                            batch_results.append((queued_url, result, None))
                        else:
                            batch_results.append((queued_url, None, "Crawl failed"))
                    
                    except Exception as e:
                        batch_results.append((queued_url, None, str(e)))
                
                return batch_results
        
        # Create clean event loop for processing
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Process URLs in batches
            while queue_manager.crawl_budget.remaining_budget > 0:
                # Get next batch
                batch = loop.run_until_complete(
                    queue_manager.get_next_batch(batch_size)
                )
                
                if not batch:
                    break  # No more URLs to process
                
                # Process batch
                batch_results = loop.run_until_complete(_process_batch(batch))
                
                # Store results in database
                for queued_url, crawl_result, error in batch_results:
                    try:
                        if crawl_result and not error:
                            # Process successful crawl
                            page_data = self._process_single_page_sync(
                                db, scan, queued_url, crawl_result
                            )
                            pages_scanned += 1
                            total_issues += page_data.get('issues_count', 0)
                            
                            # Mark as completed
                            loop.run_until_complete(
                                queue_manager.mark_completed(queued_url.url, success=True)
                            )
                        else:
                            # Handle failure
                            pages_failed += 1
                            loop.run_until_complete(
                                queue_manager.mark_completed(
                                    queued_url.url, success=False, error=error
                                )
                            )
                            
                    except Exception as process_error:
                        logger.error(f"Error processing {queued_url.url}: {process_error}")
                        pages_failed += 1
                        loop.run_until_complete(
                            queue_manager.mark_completed(
                                queued_url.url, success=False, error=str(process_error)
                            )
                        )
                
                # Commit batch to database
                db.commit()
                
                logger.info(f"Processed batch: {len(batch)} URLs, "
                          f"Total: {pages_scanned} scanned, {pages_failed} failed")
        
        finally:
            loop.close()
            asyncio.set_event_loop(None)
        
        return {
            'pages_scanned': pages_scanned,
            'pages_failed': pages_failed,
            'total_issues': total_issues,
            'processing_method': 'priority_queue',
            'queue_statistics': queue_manager.get_queue_status()
        }
    
    def _process_single_page_sync(
        self, 
        db: Session, 
        scan: Scan, 
        queued_url: QueuedURL, 
        crawl_result: Any
    ) -> Dict[str, Any]:
        """Process a single page and store results with URL discovery metadata"""
        
        # Clean URL
        clean_page_url = clean_url(crawl_result.url)
        
        # Check if page already exists
        existing_page = db.query(Page).filter(
            Page.scan_id == scan.id,
            Page.url == clean_page_url
        ).first()
        
        if existing_page:
            logger.debug(f"Page already exists: {clean_page_url}")
            return {'issues_count': existing_page.issues_count}
        
        # Run SEO analysis
        analysis_result = self.seo_analyzer.analyze_page(crawl_result, scan.website.domain)
        
        # Create page with URL discovery metadata
        page = Page(
            scan_id=scan.id,
            url=clean_page_url,
            status_code=getattr(crawl_result, 'status_code', 200),
            response_time=getattr(crawl_result, 'response_time', 0),
            
            # SEO data
            title=analysis_result.get('title', ''),
            meta_description=analysis_result.get('meta_description', ''),
            h1_tags=analysis_result.get('h1_tags', []),
            h2_tags=analysis_result.get('h2_tags', []),
            h3_tags=analysis_result.get('h3_tags', []),
            
            # Content analysis
            word_count=analysis_result.get('word_count', 0),
            content_hash=analysis_result.get('content_hash', ''),
            
            # Scoring
            seo_score=analysis_result.get('seo_score', 0),
            performance_score=analysis_result.get('performance_score', 0),
            technical_score=analysis_result.get('technical_score', 0),
            mobile_score=analysis_result.get('mobile_score', 0),
            
            # URL Discovery Metadata (Enterprise Features)
            discovery_source=queued_url.discovered_url.source.value,
            discovery_priority=queued_url.discovered_url.calculated_priority,
            sitemap_priority=queued_url.discovered_url.sitemap_priority,
            sitemap_changefreq=queued_url.discovered_url.changefreq.freq_value if queued_url.discovered_url.changefreq else None,
            sitemap_lastmod=queued_url.discovered_url.lastmod,
            source_sitemap_url=queued_url.discovered_url.source_sitemap,
            parent_url=queued_url.discovered_url.parent_url,
            crawl_depth=queued_url.discovered_url.depth,
            
            # Processing Metadata
            queue_priority=queued_url.queue_priority.name,
            processing_started=queued_url.processing_started,
            processing_completed=datetime.utcnow(),
            estimated_processing_time=queued_url.estimated_processing_time,
            actual_processing_time=queued_url.processing_duration,
            processing_status='completed'
        )
        
        db.add(page)
        db.flush()  # Get page ID
        
        # Store issues
        issues_count = 0
        for issue_data in analysis_result.get('issues', []):
            issue = Issue(
                page_id=page.id,
                type=issue_data.get('type', 'unknown'),
                severity=issue_data.get('severity', 'low'),
                category=issue_data.get('category', 'general'),
                title=issue_data.get('title', ''),
                description=issue_data.get('description', ''),
                recommendation=issue_data.get('recommendation', ''),
                element=issue_data.get('element', ''),
                score_impact=issue_data.get('score_impact', 0)
            )
            db.add(issue)
            issues_count += 1
        
        page.issues_count = issues_count
        
        return {
            'issues_count': issues_count,
            'seo_score': page.seo_score,
            'discovery_source': page.discovery_source
        }
    
    def get_discovery_statistics(self, scan_id: int) -> Dict[str, Any]:
        """Get comprehensive URL discovery statistics for a scan"""
        with SyncSessionLocal() as db:
            # Get all pages for the scan
            pages = db.query(Page).filter(Page.scan_id == scan_id).all()
            
            if not pages:
                return {'error': 'No pages found for scan'}
            
            # Calculate statistics
            stats = {
                'total_pages': len(pages),
                'source_distribution': {},
                'priority_distribution': {},
                'processing_performance': {
                    'average_processing_time': 0,
                    'fastest_page': None,
                    'slowest_page': None
                },
                'sitemap_analysis': {
                    'sitemap_pages': 0,
                    'average_sitemap_priority': 0,
                    'changefreq_distribution': {}
                }
            }
            
            # Analyze source distribution
            for page in pages:
                source = page.discovery_source or 'unknown'
                stats['source_distribution'][source] = stats['source_distribution'].get(source, 0) + 1
                
                # Processing time analysis
                if page.actual_processing_time:
                    if not stats['processing_performance']['fastest_page'] or \
                       page.actual_processing_time < stats['processing_performance']['fastest_page']:
                        stats['processing_performance']['fastest_page'] = page.actual_processing_time
                    
                    if not stats['processing_performance']['slowest_page'] or \
                       page.actual_processing_time > stats['processing_performance']['slowest_page']:
                        stats['processing_performance']['slowest_page'] = page.actual_processing_time
                
                # Sitemap analysis
                if page.discovery_source == 'sitemap':
                    stats['sitemap_analysis']['sitemap_pages'] += 1
                    
                    if page.sitemap_changefreq:
                        freq = page.sitemap_changefreq
                        stats['sitemap_analysis']['changefreq_distribution'][freq] = \
                            stats['sitemap_analysis']['changefreq_distribution'].get(freq, 0) + 1
            
            # Calculate averages
            processing_times = [p.actual_processing_time for p in pages if p.actual_processing_time]
            if processing_times:
                stats['processing_performance']['average_processing_time'] = sum(processing_times) / len(processing_times)
            
            sitemap_priorities = [p.sitemap_priority for p in pages if p.sitemap_priority]
            if sitemap_priorities:
                stats['sitemap_analysis']['average_sitemap_priority'] = sum(sitemap_priorities) / len(sitemap_priorities)
            
            return stats