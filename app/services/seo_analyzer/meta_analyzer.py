from typing import Dict, Optional
from bs4 import BeautifulSoup

class MetaAnalyzer:
    """Analyzes meta tags and title elements"""
    
    def analyze(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract title and meta description from HTML"""
        result = {
            'title': self._extract_title(soup),
            'meta_description': self._extract_meta_description(soup)
        }
        return result
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title"""
        title_tag = soup.find('title')
        return title_tag.get_text(strip=True) if title_tag else ''
    
    def _extract_meta_description(self, soup: BeautifulSoup) -> str:
        """Extract meta description"""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            return meta_desc['content'].strip()
        return ''
    
    def get_title_issues(self, title: str) -> list:
        """Check title for common SEO issues"""
        issues = []
        
        if not title:
            issues.append({
                'type': 'missing_title',
                'severity': 'critical',
                'message': 'Page is missing a title tag'
            })
        elif len(title) < 30:
            issues.append({
                'type': 'title_too_short',
                'severity': 'medium',
                'message': f'Title is too short ({len(title)} chars). Recommended: 30-60 characters'
            })
        elif len(title) > 60:
            issues.append({
                'type': 'title_too_long',
                'severity': 'medium',
                'message': f'Title is too long ({len(title)} chars). Recommended: 30-60 characters'
            })
        
        return issues
    
    def get_meta_description_issues(self, meta_desc: str) -> list:
        """Check meta description for common SEO issues"""
        issues = []
        
        if not meta_desc:
            issues.append({
                'type': 'missing_meta_description',
                'severity': 'high',
                'message': 'Page is missing a meta description'
            })
        elif len(meta_desc) < 120:
            issues.append({
                'type': 'meta_desc_too_short',
                'severity': 'medium',
                'message': f'Meta description is too short ({len(meta_desc)} chars). Recommended: 120-160 characters'
            })
        elif len(meta_desc) > 160:
            issues.append({
                'type': 'meta_desc_too_long',
                'severity': 'medium',
                'message': f'Meta description is too long ({len(meta_desc)} chars). Recommended: 120-160 characters'
            })
        
        return issues