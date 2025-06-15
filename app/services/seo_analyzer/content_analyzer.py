from typing import Dict
from bs4 import BeautifulSoup
import re

class ContentAnalyzer:
    """Analyzes page content for SEO factors"""
    
    def analyze(self, soup: BeautifulSoup) -> Dict[str, int]:
        """Analyze page content"""
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "aside"]):
            script.decompose()
        
        # Get text content
        text = soup.get_text()
        
        # Clean up text
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        # Count words
        words = text.split()
        word_count = len(words)
        
        return {
            'word_count': word_count
        }
    
    def get_content_issues(self, word_count: int) -> list:
        """Generate content-related issues"""
        issues = []
        
        if word_count < 300:
            issues.append({
                'type': 'thin_content',
                'severity': 'medium',
                'message': f"Page has thin content ({word_count} words). Consider adding more valuable content"
            })
        
        return issues