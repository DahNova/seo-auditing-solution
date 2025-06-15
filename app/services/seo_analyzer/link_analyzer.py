from typing import Dict
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import asyncio
import aiohttp

class LinkAnalyzer:
    """Analyzes internal and external links"""
    
    def analyze(self, soup: BeautifulSoup, page_url: str, domain: str) -> Dict[str, int]:
        """Analyze all links on the page"""
        links = soup.find_all('a', href=True)
        
        internal_links = 0
        external_links = 0
        broken_links = 0
        
        for link in links:
            href = link['href'].strip()
            if not href or href.startswith('#') or href.startswith('mailto:') or href.startswith('tel:'):
                continue
            
            # Convert relative URLs to absolute
            full_url = urljoin(page_url, href)
            parsed_url = urlparse(full_url)
            
            # Check if internal or external
            if parsed_url.netloc == domain or parsed_url.netloc == f"www.{domain}" or parsed_url.netloc == domain.replace("www.", ""):
                internal_links += 1
            else:
                external_links += 1
        
        return {
            'internal_links': internal_links,
            'external_links': external_links,
            'broken_links': broken_links  # Note: broken link detection requires async HTTP requests
        }
    
    async def check_broken_links(self, soup: BeautifulSoup, page_url: str) -> int:
        """Check for broken links (async operation)"""
        links = soup.find_all('a', href=True)
        broken_count = 0
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            for link in links:
                href = link['href'].strip()
                if href and not href.startswith('#') and not href.startswith('mailto:') and not href.startswith('tel:'):
                    full_url = urljoin(page_url, href)
                    tasks.append(self._check_single_link(session, full_url))
            
            if tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                broken_count = sum(1 for result in results if result is False)
        
        return broken_count
    
    async def _check_single_link(self, session: aiohttp.ClientSession, url: str) -> bool:
        """Check if a single link is working"""
        try:
            async with session.head(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                return response.status < 400
        except:
            return False
    
    def get_link_issues(self, link_data: Dict[str, int]) -> list:
        """Generate issues based on link analysis"""
        issues = []
        
        if link_data['broken_links'] > 0:
            issues.append({
                'type': 'broken_links',
                'severity': 'high',
                'message': f"{link_data['broken_links']} broken links found"
            })
        
        if link_data['internal_links'] == 0:
            issues.append({
                'type': 'no_internal_links',
                'severity': 'medium',
                'message': "Page has no internal links"
            })
        
        return issues