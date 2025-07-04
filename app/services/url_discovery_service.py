"""
Enterprise URL Discovery Service
Multi-source URL discovery orchestrating sitemaps, crawling, and manual URLs
for comprehensive SEO auditing with intelligent prioritization.
"""
import logging
import asyncio
from typing import List, Dict, Any, Optional, Set, Tuple
from urllib.parse import urlparse, urljoin
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from .sitemap_parser import SitemapParser, SitemapURL, ChangeFrequency
from app.services.url_utils import clean_url, normalize_url

logger = logging.getLogger(__name__)

class URLSource(Enum):
    """Source of URL discovery"""
    SITEMAP = "sitemap"
    CRAWL = "crawl"
    MANUAL = "manual"
    ROBOTS = "robots"
    FEED = "feed"

@dataclass
class DiscoveredURL:
    """Represents a discovered URL with metadata from all sources"""
    url: str
    source: URLSource
    priority: float = 0.5
    depth: int = 0
    parent_url: Optional[str] = None
    
    # Sitemap-specific data
    sitemap_priority: float = 0.5
    changefreq: ChangeFrequency = ChangeFrequency.MONTHLY
    lastmod: Optional[datetime] = None
    source_sitemap: Optional[str] = None
    
    # Crawling-specific data
    link_text: Optional[str] = None
    link_context: Optional[str] = None
    is_internal: bool = True
    
    # Manual/Custom data
    custom_tags: List[str] = field(default_factory=list)
    custom_priority: Optional[float] = None
    
    # Analysis metadata
    discovered_at: datetime = field(default_factory=datetime.now)
    content_type: Optional[str] = None
    estimated_importance: float = 0.5
    
    @property
    def calculated_priority(self) -> float:
        """Calculate final priority considering all factors"""
        # Start with base priority
        base_priority = self.priority
        
        # Apply custom priority if set
        if self.custom_priority is not None:
            base_priority = self.custom_priority
        
        # Sitemap priority bonus (sitemap URLs are generally more important)
        if self.source == URLSource.SITEMAP:
            sitemap_bonus = 0.2
            changefreq_bonus = self.changefreq.priority_score * 0.1
            base_priority += sitemap_bonus + changefreq_bonus
        
        # Depth penalty (deeper URLs are generally less important)
        depth_penalty = min(0.05 * self.depth, 0.3)
        base_priority -= depth_penalty
        
        # Manual URLs get priority boost
        if self.source == URLSource.MANUAL:
            base_priority += 0.3
        
        # Home page and important pages boost
        parsed = urlparse(self.url)
        path = parsed.path.lower().strip('/')
        
        if not path or path == 'index':
            base_priority += 0.2  # Homepage boost
        elif any(important in path for important in ['contact', 'about', 'services', 'products']):
            base_priority += 0.1  # Important page boost
        
        return max(0.0, min(1.0, base_priority))
    
    @property
    def domain(self) -> str:
        """Extract domain from URL"""
        return urlparse(self.url).netloc

class URLDiscoveryConfig:
    """Configuration for URL discovery process"""
    
    def __init__(self):
        # Sitemap settings
        self.use_sitemaps = True
        self.max_sitemap_urls = 50000
        self.sitemap_timeout = 60
        
        # Crawling settings
        self.use_crawling = True
        self.max_crawl_depth = 5
        self.max_crawl_pages = 1000
        self.crawl_external = False
        self.crawl_timeout = 300
        
        # URL filtering
        self.excluded_extensions = {
            '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
            '.zip', '.rar', '.tar', '.gz', '.exe', '.dmg',
            '.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp',
            '.mp3', '.mp4', '.avi', '.mov', '.wmv', '.css', '.js'
        }
        
        self.excluded_patterns = [
            r'/admin/',
            r'/wp-admin/',
            r'/wp-content/',
            r'/wp-includes/',
            r'/cache/',
            r'/temp/',
            r'/tmp/',
            r'\?.*print',
            r'\?.*download',
            r'/feed/',
            r'/rss/'
        ]
        
        # Priority settings
        self.priority_weights = {
            URLSource.MANUAL: 1.0,
            URLSource.SITEMAP: 0.8,
            URLSource.CRAWL: 0.6,
            URLSource.ROBOTS: 0.4,
            URLSource.FEED: 0.3
        }

class URLDiscoveryService:
    """Enterprise URL discovery service orchestrating multiple sources"""
    
    def __init__(self, config: URLDiscoveryConfig = None):
        self.config = config or URLDiscoveryConfig()
        self.sitemap_parser = SitemapParser()
        
    async def discover_urls(
        self, 
        domain: str,
        robots_content: str = None,
        manual_urls: List[str] = None,
        crawl_config: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Comprehensive URL discovery from all sources
        Returns prioritized URL list with metadata
        """
        discovery_results = {
            'domain': domain,
            'total_urls': 0,
            'urls': [],
            'sources': {
                'sitemap': {'count': 0, 'urls': []},
                'crawl': {'count': 0, 'urls': []},
                'manual': {'count': 0, 'urls': []}
            },
            'statistics': {
                'discovery_time': 0,
                'sitemap_success': False,
                'crawl_success': False,
                'duplicate_count': 0,
                'filtered_count': 0
            },
            'errors': []
        }
        
        start_time = datetime.now()
        discovered_urls: Dict[str, DiscoveredURL] = {}
        
        try:
            # Phase 1: Sitemap Discovery (Primary source)
            if self.config.use_sitemaps:
                logger.info(f"Starting sitemap discovery for {domain}")
                sitemap_urls = await self._discover_from_sitemaps(domain, robots_content)
                
                for url_obj in sitemap_urls:
                    discovered_url = DiscoveredURL(
                        url=url_obj.url,
                        source=URLSource.SITEMAP,
                        priority=url_obj.priority,
                        sitemap_priority=url_obj.priority,
                        changefreq=url_obj.changefreq,
                        lastmod=url_obj.lastmod,
                        source_sitemap=url_obj.source_sitemap
                    )
                    discovered_urls[url_obj.url] = discovered_url
                
                discovery_results['sources']['sitemap']['count'] = len(sitemap_urls)
                discovery_results['sources']['sitemap']['urls'] = sitemap_urls
                discovery_results['statistics']['sitemap_success'] = len(sitemap_urls) > 0
                
                logger.info(f"Discovered {len(sitemap_urls)} URLs from sitemaps")
            
            # Phase 2: Manual URLs (Highest priority)
            if manual_urls:
                logger.info(f"Processing {len(manual_urls)} manual URLs")
                manual_discovered = self._process_manual_urls(manual_urls, domain)
                
                for manual_url in manual_discovered:
                    # Manual URLs override sitemap URLs
                    discovered_urls[manual_url.url] = manual_url
                
                discovery_results['sources']['manual']['count'] = len(manual_discovered)
                discovery_results['sources']['manual']['urls'] = manual_discovered
            
            # Phase 3: Crawling Discovery (Supplementary)
            if self.config.use_crawling:
                logger.info(f"Starting crawl discovery for {domain}")
                crawl_urls = await self._discover_from_crawling(domain, list(discovered_urls.keys()), crawl_config)
                
                # Add crawled URLs that aren't already discovered
                new_crawl_urls = []
                for crawl_url in crawl_urls:
                    if crawl_url.url not in discovered_urls:
                        discovered_urls[crawl_url.url] = crawl_url
                        new_crawl_urls.append(crawl_url)
                
                discovery_results['sources']['crawl']['count'] = len(new_crawl_urls)
                discovery_results['sources']['crawl']['urls'] = new_crawl_urls
                discovery_results['statistics']['crawl_success'] = len(new_crawl_urls) > 0
                
                logger.info(f"Discovered {len(new_crawl_urls)} additional URLs from crawling")
            
            # Phase 4: URL Filtering and Validation
            filtered_urls = self._filter_and_validate_urls(list(discovered_urls.values()))
            
            # Phase 5: Priority Calculation and Sorting
            prioritized_urls = self._calculate_priorities_and_sort(filtered_urls)
            
            # Compile final results
            discovery_results['urls'] = prioritized_urls
            discovery_results['total_urls'] = len(prioritized_urls)
            discovery_results['statistics']['duplicate_count'] = len(discovered_urls) - len(filtered_urls)
            discovery_results['statistics']['filtered_count'] = len(discovered_urls) - len(prioritized_urls)
            discovery_results['statistics']['discovery_time'] = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"URL discovery complete for {domain}: {len(prioritized_urls)} final URLs")
            
        except Exception as e:
            error_msg = f"Critical error in URL discovery for {domain}: {str(e)}"
            logger.error(error_msg)
            discovery_results['errors'].append(error_msg)
        
        return discovery_results
    
    async def _discover_from_sitemaps(self, domain: str, robots_content: str = None) -> List[SitemapURL]:
        """Discover URLs from sitemaps using the sitemap parser"""
        try:
            async with self.sitemap_parser:
                sitemap_results = await self.sitemap_parser.parse_all_sitemaps(domain, robots_content)
                
                urls = sitemap_results.get('urls', [])
                logger.info(f"Sitemap parser returned {len(urls)} URLs for domain {domain}")
                
                # Apply sitemap-specific filtering
                filtered_urls = []
                filtered_out_count = 0
                for url in urls:
                    if len(filtered_urls) >= self.config.max_sitemap_urls:
                        break
                    
                    # Basic URL validation
                    if self._is_valid_url(url.url, domain):
                        filtered_urls.append(url)
                    else:
                        filtered_out_count += 1
                        if filtered_out_count <= 5:  # Log first 5 filtered URLs for debugging
                            logger.debug(f"Filtered out URL: {url.url}")
                
                logger.info(f"After filtering: {len(filtered_urls)} URLs passed validation, {filtered_out_count} filtered out")
                return filtered_urls
                
        except Exception as e:
            logger.error(f"Error in sitemap discovery for {domain}: {str(e)}")
            return []
    
    def _process_manual_urls(self, manual_urls: List[str], domain: str) -> List[DiscoveredURL]:
        """Process manually provided URLs"""
        processed_urls = []
        
        for url in manual_urls:
            # Clean and normalize URL
            clean_url_str = clean_url(url)
            
            if self._is_valid_url(clean_url_str, domain):
                discovered_url = DiscoveredURL(
                    url=clean_url_str,
                    source=URLSource.MANUAL,
                    priority=0.9,  # Manual URLs get high priority
                    custom_priority=0.9,
                    custom_tags=['manual']
                )
                processed_urls.append(discovered_url)
        
        return processed_urls
    
    async def _discover_from_crawling(
        self, 
        domain: str, 
        seed_urls: List[str], 
        crawl_config: Dict[str, Any] = None
    ) -> List[DiscoveredURL]:
        """Discover URLs through crawling (simplified implementation)"""
        # This is a simplified version - in a full implementation,
        # you would integrate with Crawl4AI or similar crawling service
        
        crawl_config = crawl_config or {}
        max_depth = crawl_config.get('max_depth', self.config.max_crawl_depth)
        max_pages = crawl_config.get('max_pages', self.config.max_crawl_pages)
        
        discovered_urls = []
        
        try:
            # Use seed URLs as starting points (or homepage if no seeds)
            if not seed_urls:
                base_url = f"https://{domain}" if not domain.startswith('http') else domain
                seed_urls = [base_url]
            
            # Simple crawling simulation - in reality, this would use Crawl4AI
            # For now, we'll generate some common URL patterns
            common_paths = [
                '/', '/about', '/contact', '/services', '/products', 
                '/blog', '/news', '/privacy', '/terms', '/sitemap'
            ]
            
            base_url = f"https://{domain}" if not domain.startswith('http') else domain
            
            for path in common_paths:
                if len(discovered_urls) >= max_pages:
                    break
                
                url = urljoin(base_url, path)
                
                if self._is_valid_url(url, domain):
                    discovered_url = DiscoveredURL(
                        url=url,
                        source=URLSource.CRAWL,
                        priority=0.5,
                        depth=1 if path != '/' else 0,
                        parent_url=base_url if path != '/' else None,
                        is_internal=True
                    )
                    discovered_urls.append(discovered_url)
            
            logger.info(f"Crawl discovery generated {len(discovered_urls)} URLs for {domain}")
            
        except Exception as e:
            logger.error(f"Error in crawl discovery for {domain}: {str(e)}")
        
        return discovered_urls
    
    def _is_valid_url(self, url: str, domain: str) -> bool:
        """Validate if URL should be included in discovery"""
        try:
            parsed = urlparse(url)
            
            # Must have valid scheme and netloc
            if not parsed.scheme or not parsed.netloc:
                return False
            
            # Must be HTTP/HTTPS
            if parsed.scheme not in ['http', 'https']:
                return False
            
            # Domain check (must match target domain or be subdomain)
            url_domain = parsed.netloc.lower()
            
            # Handle different domain input formats
            target_domain = domain.lower()
            # If domain starts with http/https, extract just the domain part
            if target_domain.startswith(('http://', 'https://')):
                target_domain = urlparse(domain).netloc.lower()
            
            # Flexible domain matching to handle www variations
            # Remove 'www.' prefix from both domains for comparison
            url_domain_clean = url_domain.replace('www.', '', 1)
            target_domain_clean = target_domain.replace('www.', '', 1)
            
            # Check if domains match (with or without www) or if URL is subdomain
            domain_matches = (
                url_domain == target_domain or  # Exact match
                url_domain_clean == target_domain_clean or  # Match without www
                url_domain.endswith(f'.{target_domain}') or  # Subdomain of target
                url_domain.endswith(f'.{target_domain_clean}')  # Subdomain without www
            )
            
            if not domain_matches:
                logger.debug(f"Domain mismatch: {url_domain} vs {target_domain}")
                return False
            
            # Extension filtering
            path = parsed.path.lower()
            for ext in self.config.excluded_extensions:
                if path.endswith(ext):
                    return False
            
            # Pattern filtering
            import re
            full_url = url.lower()
            for pattern in self.config.excluded_patterns:
                if re.search(pattern, full_url):
                    return False
            
            return True
            
        except Exception:
            return False
    
    def _filter_and_validate_urls(self, urls: List[DiscoveredURL]) -> List[DiscoveredURL]:
        """Filter and validate discovered URLs"""
        seen_urls = set()
        filtered_urls = []
        
        for url in urls:
            # Normalize URL for deduplication
            normalized = normalize_url(url.url)
            
            if normalized not in seen_urls:
                seen_urls.add(normalized)
                url.url = normalized  # Update with normalized version
                filtered_urls.append(url)
        
        return filtered_urls
    
    def _calculate_priorities_and_sort(self, urls: List[DiscoveredURL]) -> List[DiscoveredURL]:
        """Calculate final priorities and sort URLs"""
        # Calculate priorities for all URLs
        for url in urls:
            # Use the calculated_priority property which considers all factors
            url.estimated_importance = url.calculated_priority
        
        # Sort by priority (highest first)
        sorted_urls = sorted(urls, key=lambda x: x.estimated_importance, reverse=True)
        
        return sorted_urls
    
    def get_priority_queue(self, urls: List[DiscoveredURL], max_urls: int = None) -> List[DiscoveredURL]:
        """Get a priority-sorted queue of URLs for scanning"""
        # Sort by calculated priority
        priority_queue = sorted(urls, key=lambda x: x.calculated_priority, reverse=True)
        
        if max_urls:
            priority_queue = priority_queue[:max_urls]
        
        return priority_queue
    
    async def refresh_url_discovery(
        self, 
        domain: str, 
        existing_urls: List[str] = None,
        robots_content: str = None
    ) -> Dict[str, Any]:
        """
        Refresh URL discovery to find new URLs
        Useful for incremental crawling and sitemap updates
        """
        logger.info(f"Refreshing URL discovery for {domain}")
        
        # Discover all URLs again
        full_discovery = await self.discover_urls(domain, robots_content)
        
        # If we have existing URLs, identify new ones
        if existing_urls:
            existing_set = set(existing_urls)
            new_urls = []
            
            for url in full_discovery['urls']:
                if url.url not in existing_set:
                    new_urls.append(url)
            
            return {
                'domain': domain,
                'new_urls': new_urls,
                'total_new': len(new_urls),
                'total_existing': len(existing_urls),
                'refresh_time': datetime.now().isoformat()
            }
        
        return full_discovery

    def export_url_list(self, urls: List[DiscoveredURL], format: str = 'json') -> str:
        """Export discovered URLs in various formats"""
        if format == 'txt':
            return '\n'.join(url.url for url in urls)
        elif format == 'csv':
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(['URL', 'Source', 'Priority', 'Depth', 'Changefreq', 'Last Modified'])
            
            for url in urls:
                writer.writerow([
                    url.url,
                    url.source.value,
                    url.calculated_priority,
                    url.depth,
                    url.changefreq.freq_value if url.changefreq else '',
                    url.lastmod.isoformat() if url.lastmod else ''
                ])
            
            return output.getvalue()
        else:  # JSON format
            import json
            
            url_data = []
            for url in urls:
                url_data.append({
                    'url': url.url,
                    'source': url.source.value,
                    'priority': url.calculated_priority,
                    'depth': url.depth,
                    'changefreq': url.changefreq.freq_value if url.changefreq else None,
                    'lastmod': url.lastmod.isoformat() if url.lastmod else None,
                    'discovered_at': url.discovered_at.isoformat()
                })
            
            return json.dumps(url_data, indent=2)