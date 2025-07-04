"""
Technical Tags Analyzer
Analyzes technical SEO tags like canonical, robots, viewport, etc.
"""
from typing import Dict, List, Any, Optional
import logging
import re
from urllib.parse import urlparse, urljoin
from app.services.url_utils import clean_url, normalize_url

logger = logging.getLogger(__name__)

class TechnicalTagsAnalyzer:
    """Analyzes technical SEO tags and directives"""
    
    def __init__(self):
        # Technical SEO factors
        self.technical_factors = {
            'canonical_url': {'importance': 'high'},
            'robots_meta': {'importance': 'high'},
            'viewport_meta': {'importance': 'high'},
            'charset_meta': {'importance': 'medium'},
            'lang_attribute': {'importance': 'medium'},
            'hreflang_tags': {'importance': 'medium'},
            'dns_prefetch': {'importance': 'low'},
            'preconnect': {'importance': 'low'},
            'preload_tags': {'importance': 'medium'}
        }
    
    def analyze_technical_tags(self, crawl_result, domain: str) -> Dict[str, Any]:
        """Analyze technical SEO tags and meta elements"""
        tech_data = {
            'canonical': {
                'present': False,
                'url': None,
                'is_self_referencing': False,
                'is_valid': True,
                'issues': []
            },
            'robots_meta': {
                'present': False,
                'content': None,
                'directives': [],
                'issues': []
            },
            'viewport': {
                'present': False,
                'content': None,
                'is_mobile_friendly': False,
                'issues': []
            },
            'charset': {
                'present': False,
                'encoding': None,
                'is_utf8': False
            },
            'lang_attr': {
                'present': False,
                'value': None,
                'is_valid': True
            },
            'hreflang': {
                'present': False,
                'tags': [],
                'languages': [],
                'issues': []
            },
            'resource_hints': {
                'dns_prefetch': [],
                'preconnect': [],
                'preload': [],
                'prefetch': []
            },
            'technical_score': 0
        }
        
        try:
            html_content = getattr(crawl_result, 'html', '')
            page_url = getattr(crawl_result, 'url', '')
            
            if not html_content:
                return tech_data
            
            # Analyze canonical URL
            tech_data['canonical'] = self._analyze_canonical(html_content, page_url, domain)
            
            # Analyze robots meta
            tech_data['robots_meta'] = self._analyze_robots_meta(html_content)
            
            # Analyze viewport
            tech_data['viewport'] = self._analyze_viewport(html_content)
            
            # Analyze charset
            tech_data['charset'] = self._analyze_charset(html_content)
            
            # Analyze lang attribute
            tech_data['lang_attr'] = self._analyze_lang_attribute(html_content)
            
            # Analyze hreflang tags
            tech_data['hreflang'] = self._analyze_hreflang(html_content)
            
            # Analyze resource hints
            tech_data['resource_hints'] = self._analyze_resource_hints(html_content)
            
            # Calculate technical score
            tech_data['technical_score'] = self._calculate_technical_score(tech_data)
            
        except Exception as e:
            logger.error(f"Error analyzing technical tags: {str(e)}")
            tech_data['error'] = str(e)
        
        return tech_data
    
    def _analyze_canonical(self, html_content: str, page_url: str, domain: str) -> Dict[str, Any]:
        """Analyze canonical URL tag"""
        canonical_data = {
            'present': False,
            'url': None,
            'is_self_referencing': False,
            'is_valid': True,
            'issues': []
        }
        
        # Extract canonical URL
        canonical_pattern = r'<link[^>]*rel=["\']canonical["\'][^>]*href=["\']([^"\']+)["\'][^>]*/?>'
        match = re.search(canonical_pattern, html_content, re.IGNORECASE)
        
        if match:
            canonical_url = match.group(1).strip()
            canonical_data['present'] = True
            canonical_data['url'] = canonical_url
            
            # Clean and normalize URLs for comparison
            try:
                clean_canonical = clean_url(canonical_url)
                clean_page_url = clean_url(page_url)
                
                # Check if self-referencing
                canonical_data['is_self_referencing'] = normalize_url(clean_canonical) == normalize_url(clean_page_url)
                
                # Validate canonical URL
                if not canonical_url.startswith(('http://', 'https://')):
                    canonical_data['issues'].append("Canonical URL should be absolute")
                    canonical_data['is_valid'] = False
                
                if domain and domain not in canonical_url:
                    canonical_data['issues'].append("Canonical URL points to different domain")
                
                # Check for common issues
                if '#' in canonical_url:
                    canonical_data['issues'].append("Canonical URL contains fragment identifier")
                
                if '?' in canonical_url and 'utm_' in canonical_url:
                    canonical_data['issues'].append("Canonical URL contains tracking parameters")
                    
            except Exception as e:
                canonical_data['issues'].append(f"Error validating canonical URL: {str(e)}")
                canonical_data['is_valid'] = False
        
        return canonical_data
    
    def _analyze_robots_meta(self, html_content: str) -> Dict[str, Any]:
        """Analyze robots meta tag"""
        robots_data = {
            'present': False,
            'content': None,
            'directives': [],
            'issues': []
        }
        
        # Extract robots meta tag
        robots_pattern = r'<meta[^>]*name=["\']robots["\'][^>]*content=["\']([^"\']*)["\'][^>]*/?>'
        match = re.search(robots_pattern, html_content, re.IGNORECASE)
        
        if match:
            robots_content = match.group(1).strip()
            robots_data['present'] = True
            robots_data['content'] = robots_content
            
            # Parse directives
            directives = [d.strip().lower() for d in robots_content.split(',')]
            robots_data['directives'] = directives
            
            # Check for conflicting directives
            if 'index' in directives and 'noindex' in directives:
                robots_data['issues'].append("Conflicting index/noindex directives")
            
            if 'follow' in directives and 'nofollow' in directives:
                robots_data['issues'].append("Conflicting follow/nofollow directives")
            
            # Check for potentially problematic directives
            if 'noindex' in directives:
                robots_data['issues'].append("Page is set to noindex - won't appear in search results")
            
            if 'nofollow' in directives:
                robots_data['issues'].append("Page is set to nofollow - links won't be followed")
        
        return robots_data
    
    def _analyze_viewport(self, html_content: str) -> Dict[str, Any]:
        """Analyze viewport meta tag"""
        viewport_data = {
            'present': False,
            'content': None,
            'is_mobile_friendly': False,
            'issues': []
        }
        
        # Extract viewport meta tag
        viewport_pattern = r'<meta[^>]*name=["\']viewport["\'][^>]*content=["\']([^"\']*)["\'][^>]*/?>'
        match = re.search(viewport_pattern, html_content, re.IGNORECASE)
        
        if match:
            viewport_content = match.group(1).strip()
            viewport_data['present'] = True
            viewport_data['content'] = viewport_content
            
            # Check for mobile-friendly settings
            content_lower = viewport_content.lower()
            
            if 'width=device-width' in content_lower:
                viewport_data['is_mobile_friendly'] = True
            else:
                viewport_data['issues'].append("Missing 'width=device-width' for mobile optimization")
            
            if 'initial-scale=1' not in content_lower:
                viewport_data['issues'].append("Consider adding 'initial-scale=1' for consistent mobile rendering")
            
            # Check for problematic settings
            if 'user-scalable=no' in content_lower:
                viewport_data['issues'].append("'user-scalable=no' prevents users from zooming")
            
            if 'maximum-scale=1' in content_lower:
                viewport_data['issues'].append("'maximum-scale=1' may limit accessibility")
        else:
            viewport_data['issues'].append("Missing viewport meta tag - page may not render properly on mobile")
        
        return viewport_data
    
    def _analyze_charset(self, html_content: str) -> Dict[str, Any]:
        """Analyze charset meta tag"""
        charset_data = {
            'present': False,
            'encoding': None,
            'is_utf8': False
        }
        
        # Extract charset from meta tag
        charset_patterns = [
            r'<meta[^>]*charset=["\']([^"\']+)["\'][^>]*/?>', 
            r'<meta[^>]*http-equiv=["\']content-type["\'][^>]*content=["\'][^"\']*charset=([^"\';\s]+)[^"\']*["\'][^>]*/?>'
        ]
        
        for pattern in charset_patterns:
            match = re.search(pattern, html_content, re.IGNORECASE)
            if match:
                charset = match.group(1).strip().lower()
                charset_data['present'] = True
                charset_data['encoding'] = charset
                charset_data['is_utf8'] = charset in ['utf-8', 'utf8']
                break
        
        return charset_data
    
    def _analyze_lang_attribute(self, html_content: str) -> Dict[str, Any]:
        """Analyze lang attribute on html element"""
        lang_data = {
            'present': False,
            'value': None,
            'is_valid': True
        }
        
        # Extract lang attribute from html tag
        lang_pattern = r'<html[^>]*lang=["\']([^"\']+)["\'][^>]*>'
        match = re.search(lang_pattern, html_content, re.IGNORECASE)
        
        if match:
            lang_value = match.group(1).strip()
            lang_data['present'] = True
            lang_data['value'] = lang_value
            
            # Basic validation (ISO 639-1 language codes)
            if len(lang_value) < 2:
                lang_data['is_valid'] = False
        
        return lang_data
    
    def _analyze_hreflang(self, html_content: str) -> Dict[str, Any]:
        """Analyze hreflang tags"""
        hreflang_data = {
            'present': False,
            'tags': [],
            'languages': [],
            'issues': []
        }
        
        # Extract hreflang links
        hreflang_pattern = r'<link[^>]*rel=["\']alternate["\'][^>]*hreflang=["\']([^"\']+)["\'][^>]*href=["\']([^"\']+)["\'][^>]*/?>'
        matches = re.findall(hreflang_pattern, html_content, re.IGNORECASE)
        
        if matches:
            hreflang_data['present'] = True
            
            for hreflang, href in matches:
                hreflang_data['tags'].append({
                    'hreflang': hreflang,
                    'href': href
                })
                
                if hreflang not in hreflang_data['languages']:
                    hreflang_data['languages'].append(hreflang)
            
            # Check for x-default
            has_x_default = any(tag['hreflang'] == 'x-default' for tag in hreflang_data['tags'])
            if not has_x_default and len(hreflang_data['languages']) > 1:
                hreflang_data['issues'].append("Consider adding 'x-default' hreflang for international targeting")
            
            # Check for self-referencing
            # This would need the current page URL to validate properly
            
        return hreflang_data
    
    def _analyze_resource_hints(self, html_content: str) -> Dict[str, List[str]]:
        """Analyze resource hints (dns-prefetch, preconnect, preload, prefetch)"""
        hints = {
            'dns_prefetch': [],
            'preconnect': [],
            'preload': [],
            'prefetch': []
        }
        
        # Extract resource hints
        hint_patterns = {
            'dns_prefetch': r'<link[^>]*rel=["\']dns-prefetch["\'][^>]*href=["\']([^"\']+)["\'][^>]*/?>',
            'preconnect': r'<link[^>]*rel=["\']preconnect["\'][^>]*href=["\']([^"\']+)["\'][^>]*/?>',
            'preload': r'<link[^>]*rel=["\']preload["\'][^>]*href=["\']([^"\']+)["\'][^>]*/?>', 
            'prefetch': r'<link[^>]*rel=["\']prefetch["\'][^>]*href=["\']([^"\']+)["\'][^>]*/?>'
        }
        
        for hint_type, pattern in hint_patterns.items():
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            hints[hint_type] = matches
        
        return hints
    
    def _calculate_technical_score(self, tech_data: Dict[str, Any]) -> float:
        """Calculate technical SEO score"""
        score = 0.0
        max_score = 100.0
        
        # Canonical URL (25 points)
        if tech_data['canonical']['present']:
            score += 15.0
            if tech_data['canonical']['is_self_referencing']:
                score += 5.0
            if tech_data['canonical']['is_valid']:
                score += 5.0
        
        # Robots meta (20 points)
        if tech_data['robots_meta']['present']:
            score += 10.0
            if not tech_data['robots_meta']['issues']:
                score += 10.0
        else:
            score += 15.0  # Default behavior is often fine
        
        # Viewport (20 points)
        if tech_data['viewport']['present']:
            score += 10.0
            if tech_data['viewport']['is_mobile_friendly']:
                score += 10.0
        
        # Charset (15 points)
        if tech_data['charset']['present']:
            score += 7.0
            if tech_data['charset']['is_utf8']:
                score += 8.0
        
        # Lang attribute (10 points)
        if tech_data['lang_attr']['present']:
            score += 5.0
            if tech_data['lang_attr']['is_valid']:
                score += 5.0
        
        # Hreflang (5 points)
        if tech_data['hreflang']['present']:
            score += 3.0
            if not tech_data['hreflang']['issues']:
                score += 2.0
        
        # Resource hints (5 points)
        total_hints = sum(len(hints) for hints in tech_data['resource_hints'].values())
        if total_hints > 0:
            score += min(total_hints, 5.0)
        
        return min(score, max_score)
    
    def extract_canonical_url(self, crawl_result) -> Optional[str]:
        """Extract canonical URL from page"""
        try:
            html_content = getattr(crawl_result, 'html', '')
            if not html_content:
                return None
            
            canonical_pattern = r'<link[^>]*rel=["\']canonical["\'][^>]*href=["\']([^"\']+)["\'][^>]*/?>'
            match = re.search(canonical_pattern, html_content, re.IGNORECASE)
            
            if match:
                canonical_url = match.group(1).strip()
                return clean_url(canonical_url)
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting canonical URL: {str(e)}")
            return None