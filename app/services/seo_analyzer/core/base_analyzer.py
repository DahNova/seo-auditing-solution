"""
Abstract Base Analyzer for SEO Analysis
Provides common patterns and utilities to avoid code duplication
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class AnalysisResult:
    """Standard analysis result structure"""
    scores: Dict[str, float]
    issues: List[Dict[str, Any]]
    opportunities: List[Dict[str, Any]]
    metadata: Dict[str, Any]

class BaseAnalyzer(ABC):
    """Abstract base class for all SEO analyzers"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    @abstractmethod
    def analyze(self, crawl_result, **kwargs) -> AnalysisResult:
        """Main analysis method - must be implemented by subclasses"""
        pass
    
    def extract_html_content(self, crawl_result) -> str:
        """Extract HTML content with fallback"""
        return getattr(crawl_result, 'html', '') or getattr(crawl_result, 'cleaned_html', '')
    
    def extract_text_content(self, crawl_result) -> str:
        """Extract clean text content"""
        html_content = self.extract_html_content(crawl_result)
        if html_content:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            return soup.get_text(separator=' ', strip=True)
        
        # Fallback to markdown
        markdown_content = getattr(crawl_result, 'markdown', '')
        if hasattr(markdown_content, 'raw_markdown'):
            return markdown_content.raw_markdown
        return str(markdown_content) if markdown_content else ''
    
    def safe_execute(self, func, *args, default=None, **kwargs):
        """Safely execute function with error handling"""
        try:
            return func(*args, **kwargs)
        except Exception as e:
            self.logger.warning(f"Error in {func.__name__}: {str(e)}")
            return default
    
    def create_issue(self, type_name: str, severity: str, category: str, 
                    title: str, description: str, recommendation: str,
                    score_impact: float = 0.0, **kwargs) -> Dict[str, Any]:
        """Create standardized issue dict"""
        return {
            'type': type_name,
            'severity': severity,
            'category': category,
            'title': title,
            'description': description,
            'recommendation': recommendation,
            'score_impact': score_impact,
            **kwargs
        }
    
    def create_opportunity(self, category: str, title: str, description: str,
                          impact: str, effort: str, implementation: str) -> Dict[str, Any]:
        """Create standardized opportunity dict"""
        return {
            'category': category,
            'title': title,
            'description': description,
            'impact': impact,
            'effort': effort,
            'implementation': implementation
        }