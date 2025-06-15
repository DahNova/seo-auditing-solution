from typing import Dict, List
from bs4 import BeautifulSoup

class HeadingAnalyzer:
    """Analyzes heading structure (H1, H2, H3, etc.)"""
    
    def analyze(self, soup: BeautifulSoup) -> Dict[str, List[str]]:
        """Extract all heading tags and their hierarchy"""
        result = {
            'h1_tags': self._extract_headings(soup, 'h1'),
            'h2_tags': self._extract_headings(soup, 'h2'),
            'h3_tags': self._extract_headings(soup, 'h3')
        }
        return result
    
    def _extract_headings(self, soup: BeautifulSoup, tag_name: str) -> List[str]:
        """Extract text from specific heading tags"""
        headings = soup.find_all(tag_name)
        return [h.get_text(strip=True) for h in headings if h.get_text(strip=True)]
    
    def get_heading_issues(self, h1_tags: List[str], h2_tags: List[str], h3_tags: List[str]) -> list:
        """Check heading structure for SEO issues"""
        issues = []
        
        # H1 tag issues
        if not h1_tags:
            issues.append({
                'type': 'missing_h1',
                'severity': 'high',
                'message': 'Page is missing an H1 tag'
            })
        elif len(h1_tags) > 1:
            issues.append({
                'type': 'multiple_h1',
                'severity': 'medium',
                'message': f'Page has {len(h1_tags)} H1 tags. Recommended: exactly 1 H1 per page'
            })
        
        # Check H1 length
        if h1_tags:
            h1_text = h1_tags[0]
            if len(h1_text) < 20:
                issues.append({
                    'type': 'h1_too_short',
                    'severity': 'low',
                    'message': f'H1 is too short ({len(h1_text)} chars). Consider making it more descriptive'
                })
            elif len(h1_text) > 70:
                issues.append({
                    'type': 'h1_too_long',
                    'severity': 'low',
                    'message': f'H1 is too long ({len(h1_text)} chars). Consider shortening it'
                })
        
        # Check heading hierarchy
        if h3_tags and not h2_tags:
            issues.append({
                'type': 'broken_heading_hierarchy',
                'severity': 'medium',
                'message': 'Page has H3 tags without H2 tags. Maintain proper heading hierarchy'
            })
        
        return issues