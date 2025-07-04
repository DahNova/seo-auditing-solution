"""
Enterprise Sitemap Parser
Comprehensive XML sitemap parsing with support for sitemap indexes, priority extraction,
and multi-format sitemap discovery for professional SEO auditing.
"""
import logging
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional, Tuple, Set
from urllib.parse import urljoin, urlparse
from dataclasses import dataclass
from datetime import datetime
import asyncio
import aiohttp
from enum import Enum
import gzip
import io
import re

logger = logging.getLogger(__name__)

class ChangeFrequency(Enum):
    """Standard sitemap changefreq values with priority scoring"""
    ALWAYS = ("always", 1.0)
    HOURLY = ("hourly", 0.9)
    DAILY = ("daily", 0.8)
    WEEKLY = ("weekly", 0.6)
    MONTHLY = ("monthly", 0.4)
    YEARLY = ("yearly", 0.2)
    NEVER = ("never", 0.1)
    
    def __init__(self, value: str, score: float):
        self.freq_value = value
        self.priority_score = score
    
    @classmethod
    def from_string(cls, freq_str: str) -> 'ChangeFrequency':
        """Convert string to ChangeFrequency enum"""
        freq_str = freq_str.lower().strip()
        for freq in cls:
            if freq.freq_value == freq_str:
                return freq
        return cls.MONTHLY  # Default fallback

@dataclass
class SitemapURL:
    """Represents a single URL from a sitemap with all metadata"""
    url: str
    priority: float = 0.5
    changefreq: ChangeFrequency = ChangeFrequency.MONTHLY
    lastmod: Optional[datetime] = None
    source_sitemap: str = ""
    is_image: bool = False
    image_data: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.image_data is None:
            self.image_data = {}
    
    @property
    def calculated_priority(self) -> float:
        """Calculate weighted priority combining sitemap priority and changefreq"""
        # Base sitemap priority (0.0-1.0)
        base_priority = self.priority
        
        # Changefreq multiplier
        freq_multiplier = self.changefreq.priority_score
        
        # Recency bonus (if lastmod is recent)
        recency_bonus = 0.0
        if self.lastmod:
            # Handle timezone-aware vs naive datetime comparison
            now = datetime.now()
            lastmod = self.lastmod
            
            # Convert both to naive datetime for comparison
            if lastmod.tzinfo is not None:
                lastmod = lastmod.replace(tzinfo=None)
            if now.tzinfo is not None:
                now = now.replace(tzinfo=None)
            
            try:
                days_since_mod = (now - lastmod).days
                if days_since_mod <= 1:
                    recency_bonus = 0.2
                elif days_since_mod <= 7:
                    recency_bonus = 0.1
                elif days_since_mod <= 30:
                    recency_bonus = 0.05
            except (TypeError, ValueError):
                # If datetime comparison still fails, skip recency bonus
                recency_bonus = 0.0
        
        # URL depth penalty (deeper URLs get lower priority)
        path_segments = len([p for p in urlparse(self.url).path.split('/') if p])
        depth_penalty = min(0.1 * path_segments, 0.3)
        
        # Calculate final priority (0.0-1.0 range)
        final_priority = (base_priority * freq_multiplier) + recency_bonus - depth_penalty
        return max(0.0, min(1.0, final_priority))

@dataclass 
class SitemapIndex:
    """Represents a sitemap index file with child sitemaps"""
    url: str
    sitemaps: List[Dict[str, Any]]
    total_sitemaps: int = 0
    
    def __post_init__(self):
        self.total_sitemaps = len(self.sitemaps)

class SitemapParser:
    """Enterprise-grade sitemap parser with comprehensive format support"""
    
    def __init__(self, max_concurrent_requests: int = 10, timeout: int = 30):
        self.max_concurrent = max_concurrent_requests
        self.timeout = timeout
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Common sitemap locations to check
        self.common_sitemap_paths = [
            '/sitemap.xml',
            '/sitemap_index.xml', 
            '/sitemaps.xml',
            '/sitemap-index.xml',
            '/sitemaps/sitemap.xml',
            '/wp-sitemap.xml',  # WordPress
            '/sitemap/sitemap.xml',
            '/site-map.xml'
        ]
        
        # XML namespaces for different sitemap formats
        self.namespaces = {
            'sitemap': 'http://www.sitemaps.org/schemas/sitemap/0.9',
            'image': 'http://www.google.com/schemas/sitemap-image/1.1',
            'video': 'http://www.google.com/schemas/sitemap-video/1.1',
            'news': 'http://www.google.com/schemas/sitemap-news/0.9',
            'mobile': 'http://www.google.com/schemas/sitemap-mobile/1.0'
        }
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout),
            headers={'User-Agent': 'SEO-Audit-Bot/1.0 (+https://seo-audit.ai/bot)'}
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def discover_sitemaps(self, domain: str, robots_content: str = None) -> List[str]:
        """
        Discover all sitemap URLs for a domain using multiple methods:
        1. Parse robots.txt for sitemap directives
        2. Check common sitemap locations
        3. Return prioritized list of found sitemaps
        """
        discovered_sitemaps = []
        base_url = f"https://{domain}" if not domain.startswith('http') else domain
        
        # Method 1: Parse robots.txt for sitemap directives
        if robots_content:
            robots_sitemaps = self._parse_robots_sitemaps(robots_content, base_url)
            discovered_sitemaps.extend(robots_sitemaps)
            logger.info(f"Found {len(robots_sitemaps)} sitemaps in robots.txt for {domain}")
        
        # Method 2: Check common sitemap locations
        common_sitemaps = await self._check_common_sitemap_locations(base_url)
        
        # Add common sitemaps that aren't already in robots.txt
        for sitemap_url in common_sitemaps:
            if sitemap_url not in discovered_sitemaps:
                discovered_sitemaps.append(sitemap_url)
        
        logger.info(f"Total discovered sitemaps for {domain}: {len(discovered_sitemaps)}")
        return discovered_sitemaps
    
    def _parse_robots_sitemaps(self, robots_content: str, base_url: str) -> List[str]:
        """Extract sitemap URLs from robots.txt content"""
        sitemaps = []
        
        for line in robots_content.split('\n'):
            line = line.strip()
            if line.lower().startswith('sitemap:'):
                sitemap_url = line[8:].strip()  # Remove 'sitemap:' prefix
                
                # Handle relative URLs
                if sitemap_url.startswith('/'):
                    sitemap_url = urljoin(base_url, sitemap_url)
                elif not sitemap_url.startswith('http'):
                    sitemap_url = urljoin(base_url, sitemap_url)
                
                sitemaps.append(sitemap_url)
        
        return sitemaps
    
    async def _check_common_sitemap_locations(self, base_url: str) -> List[str]:
        """Check common sitemap locations and return found URLs"""
        found_sitemaps = []
        
        # Create semaphore for concurrent requests
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async def check_sitemap_url(path: str) -> Optional[str]:
            """Check if a sitemap exists at the given path"""
            async with semaphore:
                try:
                    full_url = urljoin(base_url, path)
                    async with self.session.head(full_url) as response:
                        if response.status == 200:
                            content_type = response.headers.get('content-type', '').lower()
                            if any(ct in content_type for ct in ['xml', 'text', 'application']):
                                return full_url
                except Exception as e:
                    logger.debug(f"Failed to check sitemap at {full_url}: {str(e)}")
            return None
        
        # Check all common paths concurrently
        tasks = [check_sitemap_url(path) for path in self.common_sitemap_paths]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Collect successful results
        for result in results:
            if isinstance(result, str):
                found_sitemaps.append(result)
        
        return found_sitemaps
    
    async def parse_sitemap(self, sitemap_url: str) -> Tuple[List[SitemapURL], Optional[SitemapIndex]]:
        """
        Parse a single sitemap URL and return URLs and index info
        Handles both sitemap indexes and regular sitemaps
        """
        try:
            content = await self._fetch_sitemap_content(sitemap_url)
            if not content:
                return [], None
            
            # Determine sitemap type and parse accordingly
            root = ET.fromstring(content)
            
            # Check if it's a sitemap index
            if self._is_sitemap_index(root):
                sitemap_index = self._parse_sitemap_index(root, sitemap_url)
                return [], sitemap_index
            else:
                # Regular sitemap with URLs
                urls = self._parse_sitemap_urls(root, sitemap_url)
                return urls, None
                
        except Exception as e:
            logger.error(f"Error parsing sitemap {sitemap_url}: {str(e)}")
            return [], None
    
    async def _fetch_sitemap_content(self, sitemap_url: str) -> Optional[str]:
        """Fetch and decompress sitemap content"""
        try:
            async with self.session.get(sitemap_url) as response:
                if response.status != 200:
                    logger.warning(f"Sitemap {sitemap_url} returned status {response.status}")
                    return None
                
                content = await response.read()
                
                # Handle gzipped sitemaps
                if sitemap_url.endswith('.gz') or response.headers.get('content-encoding') == 'gzip':
                    try:
                        content = gzip.decompress(content)
                    except Exception as e:
                        logger.debug(f"Failed to decompress gzipped sitemap {sitemap_url}: {str(e)}")
                
                return content.decode('utf-8', errors='ignore')
                
        except Exception as e:
            logger.error(f"Failed to fetch sitemap {sitemap_url}: {str(e)}")
            return None
    
    def _is_sitemap_index(self, root: ET.Element) -> bool:
        """Determine if XML is a sitemap index or regular sitemap"""
        # Check for sitemapindex tag
        if root.tag.endswith('sitemapindex'):
            return True
        
        # Check for sitemap children (indicates index)
        for child in root:
            if child.tag.endswith('sitemap'):
                return True
        
        return False
    
    def _parse_sitemap_index(self, root: ET.Element, source_url: str) -> SitemapIndex:
        """Parse sitemap index and extract child sitemap information"""
        sitemaps = []
        
        for sitemap_elem in root.iter():
            if sitemap_elem.tag.endswith('sitemap'):
                sitemap_info = {}
                
                for child in sitemap_elem:
                    tag_name = child.tag.split('}')[-1]  # Remove namespace
                    
                    if tag_name == 'loc':
                        sitemap_info['url'] = child.text.strip() if child.text else ""
                    elif tag_name == 'lastmod':
                        sitemap_info['lastmod'] = self._parse_datetime(child.text)
                
                if sitemap_info.get('url'):
                    sitemaps.append(sitemap_info)
        
        return SitemapIndex(url=source_url, sitemaps=sitemaps)
    
    def _parse_sitemap_urls(self, root: ET.Element, source_url: str) -> List[SitemapURL]:
        """Parse regular sitemap and extract URL information"""
        urls = []
        
        for url_elem in root.iter():
            if url_elem.tag.endswith('url'):
                url_data = self._extract_url_data(url_elem, source_url)
                if url_data:
                    urls.append(url_data)
        
        return urls
    
    def _extract_url_data(self, url_elem: ET.Element, source_sitemap: str) -> Optional[SitemapURL]:
        """Extract URL data from a single <url> element"""
        url_data = {
            'url': '',
            'priority': 0.5,
            'changefreq': ChangeFrequency.MONTHLY,
            'lastmod': None,
            'source_sitemap': source_sitemap,
            'is_image': False,
            'image_data': {}
        }
        
        for child in url_elem:
            tag_name = child.tag.split('}')[-1]  # Remove namespace
            
            if tag_name == 'loc':
                url_data['url'] = child.text.strip() if child.text else ""
            elif tag_name == 'priority':
                try:
                    url_data['priority'] = float(child.text) if child.text else 0.5
                except (ValueError, TypeError):
                    url_data['priority'] = 0.5
            elif tag_name == 'changefreq':
                url_data['changefreq'] = ChangeFrequency.from_string(child.text or "")
            elif tag_name == 'lastmod':
                url_data['lastmod'] = self._parse_datetime(child.text)
            elif tag_name == 'image':
                # Handle image sitemap extensions
                image_info = self._parse_image_data(child)
                if image_info:
                    url_data['is_image'] = True
                    url_data['image_data'] = image_info
        
        # Validate required URL field
        if not url_data['url']:
            return None
        
        return SitemapURL(**url_data)
    
    def _parse_image_data(self, image_elem: ET.Element) -> Dict[str, Any]:
        """Parse image sitemap extension data"""
        image_data = {}
        
        for child in image_elem:
            tag_name = child.tag.split('}')[-1]
            
            if tag_name == 'loc':
                image_data['image_url'] = child.text.strip() if child.text else ""
            elif tag_name == 'caption':
                image_data['caption'] = child.text.strip() if child.text else ""
            elif tag_name == 'title':
                image_data['title'] = child.text.strip() if child.text else ""
            elif tag_name == 'license':
                image_data['license'] = child.text.strip() if child.text else ""
        
        return image_data
    
    def _parse_datetime(self, datetime_str: str) -> Optional[datetime]:
        """Parse various datetime formats found in sitemaps with robust error handling"""
        if not datetime_str:
            return None
        
        datetime_str = datetime_str.strip()
        
        # Common datetime formats in sitemaps
        formats = [
            '%Y-%m-%dT%H:%M:%S%z',      # ISO 8601 with timezone
            '%Y-%m-%dT%H:%M:%SZ',       # ISO 8601 UTC
            '%Y-%m-%dT%H:%M:%S',        # ISO 8601 without timezone
            '%Y-%m-%d',                 # Date only
            '%Y-%m-%d %H:%M:%S',        # MySQL datetime
        ]
        
        for fmt in formats:
            try:
                parsed_date = datetime.strptime(datetime_str, fmt)
                # Additional validation for edge cases
                if parsed_date.year < 1900 or parsed_date.year > 2100:
                    logger.debug(f"Date year out of reasonable range: {datetime_str}")
                    continue
                return parsed_date
            except ValueError as e:
                # Log specific problematic dates for debugging
                if "day is out of range for month" in str(e):
                    logger.debug(f"Invalid date in sitemap: {datetime_str} - {str(e)}")
                continue
            except Exception as e:
                # Catch any other unexpected datetime parsing errors
                logger.debug(f"Unexpected error parsing datetime {datetime_str}: {str(e)}")
                continue
        
        logger.debug(f"Could not parse datetime: {datetime_str}")
        return None
    
    async def parse_all_sitemaps(self, domain: str, robots_content: str = None) -> Dict[str, Any]:
        """
        Comprehensive recursive sitemap parsing for multi-level sitemap indexes
        Handles nested sitemap indexes with circular reference protection
        """
        results = {
            'domain': domain,
            'discovered_sitemaps': [],
            'sitemap_indexes': [],
            'total_urls': 0,
            'urls': [],
            'parsing_errors': [],
            'statistics': {
                'sitemaps_found': 0,
                'sitemaps_parsed': 0,
                'indexes_found': 0,
                'max_depth': 0,
                'urls_by_priority': {},
                'urls_by_changefreq': {},
                'recent_updates': 0
            }
        }
        
        try:
            # Step 1: Discover initial sitemaps
            initial_sitemap_urls = await self.discover_sitemaps(domain, robots_content)
            results['discovered_sitemaps'] = initial_sitemap_urls
            
            if not initial_sitemap_urls:
                logger.warning(f"No sitemaps found for domain {domain}")
                return results
            
            # Step 2: Recursively parse all sitemaps with depth tracking
            all_urls = []
            all_indexes = []
            parsing_errors = []
            processed_urls = set()  # Prevent circular references
            
            parsed_data = await self._parse_sitemaps_recursive(
                initial_sitemap_urls, 
                processed_urls, 
                depth=0, 
                max_depth=5  # Prevent infinite recursion
            )
            
            all_urls = parsed_data['urls']
            all_indexes = parsed_data['indexes']
            parsing_errors = parsed_data['errors']
            
            # Step 3: Deduplicate URLs (same URL from multiple sitemaps)
            unique_urls = self._deduplicate_urls(all_urls)
            
            # Step 4: Compile final results
            results['urls'] = unique_urls
            results['sitemap_indexes'] = all_indexes
            results['parsing_errors'] = parsing_errors
            results['total_urls'] = len(unique_urls)
            results['statistics']['sitemaps_found'] = len(processed_urls)
            results['statistics']['sitemaps_parsed'] = len(processed_urls) - len(parsing_errors)
            results['statistics']['indexes_found'] = len(all_indexes)
            results['statistics']['max_depth'] = parsed_data.get('max_depth_reached', 0)
            
            # Generate comprehensive statistics
            results['statistics'].update(self._generate_url_statistics(unique_urls))
            
            logger.info(f"Recursive sitemap parsing complete for {domain}: "
                       f"{len(unique_urls)} unique URLs from {len(processed_urls)} sitemaps "
                       f"(max depth: {results['statistics']['max_depth']})")
            
        except Exception as e:
            logger.error(f"Critical error in parse_all_sitemaps for {domain}: {str(e)}")
            results['parsing_errors'].append(f"Critical parsing error: {str(e)}")
        
        return results
    
    async def _parse_sitemaps_recursive(
        self, 
        sitemap_urls: List[str], 
        processed_urls: Set[str], 
        depth: int = 0, 
        max_depth: int = 5
    ) -> Dict[str, Any]:
        """
        Recursively parse sitemaps handling multi-level sitemap indexes
        
        Args:
            sitemap_urls: List of sitemap URLs to parse
            processed_urls: Set of already processed URLs (prevents circular refs)
            depth: Current recursion depth
            max_depth: Maximum allowed recursion depth
            
        Returns:
            Dict containing all URLs, indexes, and errors from recursive parsing
        """
        if depth > max_depth:
            logger.warning(f"Maximum sitemap recursion depth ({max_depth}) reached")
            return {'urls': [], 'indexes': [], 'errors': [], 'max_depth_reached': depth}
        
        all_urls = []
        all_indexes = []
        all_errors = []
        child_sitemap_urls = []
        max_depth_reached = depth
        
        # Use semaphore to limit concurrent parsing at each level
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async def parse_single_sitemap_with_protection(sitemap_url: str):
            """Parse single sitemap with circular reference protection"""
            if sitemap_url in processed_urls:
                logger.debug(f"Skipping already processed sitemap: {sitemap_url}")
                return [], None, None
            
            processed_urls.add(sitemap_url)
            
            async with semaphore:
                try:
                    urls, index = await self.parse_sitemap(sitemap_url)
                    return urls, index, None
                except Exception as e:
                    error_msg = f"Failed to parse {sitemap_url} at depth {depth}: {str(e)}"
                    logger.error(error_msg)
                    return [], None, error_msg
        
        # Parse all sitemaps at current level concurrently
        tasks = [parse_single_sitemap_with_protection(url) for url in sitemap_urls]
        parse_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results from current level
        for i, result in enumerate(parse_results):
            if isinstance(result, Exception):
                error_msg = f"Exception parsing {sitemap_urls[i]} at depth {depth}: {str(result)}"
                all_errors.append(error_msg)
                continue
            
            urls, index, error = result
            
            if error:
                all_errors.append(error)
                continue
            
            if index:
                # This is a sitemap index - collect child sitemap URLs for next level
                all_indexes.append(index)
                logger.info(f"Found sitemap index at depth {depth}: {index.url} with {len(index.sitemaps)} child sitemaps")
                
                for sitemap_info in index.sitemaps:
                    child_url = sitemap_info.get('url')
                    if child_url and child_url not in processed_urls:
                        child_sitemap_urls.append(child_url)
            else:
                # Regular sitemap with URLs
                all_urls.extend(urls)
                if urls:
                    logger.debug(f"Parsed {len(urls)} URLs from sitemap at depth {depth}")
        
        # Recursively parse child sitemaps from indexes (next level)
        if child_sitemap_urls and depth < max_depth:
            logger.info(f"Recursively parsing {len(child_sitemap_urls)} child sitemaps at depth {depth + 1}")
            
            child_results = await self._parse_sitemaps_recursive(
                child_sitemap_urls, 
                processed_urls, 
                depth + 1, 
                max_depth
            )
            
            all_urls.extend(child_results['urls'])
            all_indexes.extend(child_results['indexes'])
            all_errors.extend(child_results['errors'])
            max_depth_reached = max(max_depth_reached, child_results.get('max_depth_reached', depth + 1))
        
        return {
            'urls': all_urls,
            'indexes': all_indexes,
            'errors': all_errors,
            'max_depth_reached': max_depth_reached
        }
    
    def _deduplicate_urls(self, urls: List[SitemapURL]) -> List[SitemapURL]:
        """
        Deduplicate URLs while preserving the highest priority entry
        When same URL appears in multiple sitemaps, keep the one with highest calculated priority
        """
        url_map = {}
        
        for sitemap_url in urls:
            url_key = sitemap_url.url
            
            if url_key in url_map:
                # Keep the URL entry with higher calculated priority
                existing = url_map[url_key]
                if sitemap_url.calculated_priority > existing.calculated_priority:
                    url_map[url_key] = sitemap_url
                    logger.debug(f"Updated URL priority: {url_key} "
                               f"({existing.calculated_priority:.3f} -> {sitemap_url.calculated_priority:.3f})")
            else:
                url_map[url_key] = sitemap_url
        
        unique_urls = list(url_map.values())
        logger.info(f"Deduplication: {len(urls)} total URLs -> {len(unique_urls)} unique URLs")
        return unique_urls
    
    def _generate_url_statistics(self, urls: List[SitemapURL]) -> Dict[str, Any]:
        """Generate comprehensive statistics about parsed URLs"""
        stats = {
            'urls_by_priority': {},
            'urls_by_changefreq': {},
            'recent_updates': 0,
            'average_priority': 0.0,
            'urls_with_images': 0,
            'priority_distribution': {
                'high': 0,      # priority >= 0.8
                'medium': 0,    # 0.4 <= priority < 0.8
                'low': 0        # priority < 0.4
            }
        }
        
        if not urls:
            return stats
        
        # Calculate distributions
        priority_sum = 0.0
        from datetime import timedelta
        recent_threshold = datetime.now().replace(hour=0, minute=0, second=0)
        recent_threshold = recent_threshold - timedelta(days=30)  # 30 days ago
        
        for url in urls:
            # Priority statistics
            priority = url.calculated_priority
            priority_sum += priority
            
            priority_bucket = f"{priority:.1f}"
            stats['urls_by_priority'][priority_bucket] = stats['urls_by_priority'].get(priority_bucket, 0) + 1
            
            # Priority distribution
            if priority >= 0.8:
                stats['priority_distribution']['high'] += 1
            elif priority >= 0.4:
                stats['priority_distribution']['medium'] += 1
            else:
                stats['priority_distribution']['low'] += 1
            
            # Changefreq statistics
            freq_name = url.changefreq.freq_value
            stats['urls_by_changefreq'][freq_name] = stats['urls_by_changefreq'].get(freq_name, 0) + 1
            
            # Recent updates
            if url.lastmod:
                try:
                    # Handle timezone-aware vs naive datetime comparison
                    lastmod = url.lastmod
                    threshold = recent_threshold
                    
                    # Convert both to naive datetime for comparison
                    if lastmod.tzinfo is not None:
                        lastmod = lastmod.replace(tzinfo=None)
                    if threshold.tzinfo is not None:
                        threshold = threshold.replace(tzinfo=None)
                    
                    if lastmod >= threshold:
                        stats['recent_updates'] += 1
                except (TypeError, ValueError):
                    # Skip comparison if datetime formats are incompatible
                    pass
            
            # Image statistics
            if url.is_image:
                stats['urls_with_images'] += 1
        
        # Calculate averages
        stats['average_priority'] = priority_sum / len(urls)
        
        return stats