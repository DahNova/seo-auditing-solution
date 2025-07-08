"""
Abstract Base Analyzer for SEO Analysis
Provides common patterns and utilities to avoid code duplication
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import logging
from dataclasses import dataclass
from app.core.issue_registry import IssueRegistry
from app.core.issue_migration import IssueMigrationUtility
from ..severity_calculator import SeverityCalculator

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
        
        # Fallback to markdown - handle both string and object types
        markdown_content = getattr(crawl_result, 'markdown', '')
        if markdown_content and hasattr(markdown_content, 'raw_markdown'):
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
        """Create standardized issue dict (LEGACY METHOD - Use create_issue_from_registry instead)"""
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
    
    def create_issue_from_registry(self, issue_type: str, context: Dict[str, Any] = None,
                                  custom_description: str = None, custom_recommendation: str = None,
                                  **kwargs) -> Dict[str, Any]:
        """
        Create issue using centralized registry (NEW PREFERRED METHOD)
        
        Args:
            issue_type: The issue type identifier (will be migrated to Italian if needed)
            context: Context data for severity calculation and escalation
            custom_description: Custom description to override registry default
            custom_recommendation: Custom recommendation to override registry default
            **kwargs: Additional fields to include in issue
            
        Returns:
            Issue dictionary with all required fields
        """
        if context is None:
            context = {}
        
        # Migrate to new Italian issue type
        migrated_type = IssueMigrationUtility.migrate_issue_type(issue_type)
        
        # Get issue definition from registry
        issue_def = IssueRegistry.get_issue(migrated_type)
        if not issue_def:
            self.logger.warning(f"Issue type '{migrated_type}' not found in registry, falling back to legacy method")
            # Fallback to old method if needed
            severity = SeverityCalculator.calculate_severity(issue_type, context)
            return self.create_issue(
                type_name=issue_type,
                severity=severity,
                category='technical_seo',  # Default category
                title=issue_type.replace('_', ' ').title(),
                description=custom_description or f'Issue detected: {issue_type}',
                recommendation=custom_recommendation or 'Please review this issue',
                score_impact=SeverityCalculator.get_severity_score(severity),
                **kwargs
            )
        
        # Calculate severity using registry
        severity = SeverityCalculator.calculate_severity_from_registry(migrated_type, context)
        
        # Build issue dictionary
        issue = {
            'type': migrated_type,  # Use migrated Italian type
            'category': issue_def.category.value,
            'severity': severity,
            'title': issue_def.name_it,
            'description': custom_description or issue_def.description_it,
            'recommendation': custom_recommendation or '; '.join(issue_def.recommendations),
            'score_impact': SeverityCalculator.get_severity_score_from_registry(migrated_type, context),
            **kwargs
        }
        
        self.logger.debug(f"Created issue '{migrated_type}' with severity '{severity}' from registry")
        return issue
    
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