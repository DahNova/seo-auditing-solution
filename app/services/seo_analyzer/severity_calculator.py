"""
Severity Calculator
Standardizes severity assignment across all SEO analyzers
"""
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class SeverityCalculator:
    """Calculates standardized severity levels for SEO issues"""
    
    # Severity hierarchy: critical > high > medium > low
    SEVERITY_WEIGHTS = {
        'critical': 4,
        'high': 3,
        'medium': 2,
        'low': 1
    }
    
    # Base severity rules by issue type
    BASE_SEVERITIES = {
        # Critical issues - site-breaking or major ranking factors
        'missing_title': 'critical',
        'missing_meta_description': 'high',
        'missing_h1': 'high',
        'crawl_error': 'critical',
        'http_error_5xx': 'critical',
        'http_error_4xx': 'high',
        
        # Performance issues - vary by resource type and location
        'blocking_css_resource': 'high',        # CSS always blocks rendering
        'blocking_js_resource': 'medium',       # Can be escalated based on location
        'slow_ttfb': 'high',
        'layout_shift_risk': 'high',
        'no_compression': 'medium',
        'large_html': 'medium',
        
        # Content quality issues
        'thin_content': 'medium',
        'poor_readability': 'medium',
        'outdated_content': 'low',
        'duplicate_content': 'high',
        'keyword_stuffing': 'medium',
        
        # Technical SEO issues
        'missing_schema_markup': 'medium',
        'poor_social_meta': 'medium',
        'missing_canonical': 'high',
        'url_structure_issue': 'medium',
        'missing_language_declaration': 'medium',
        
        # Accessibility issues
        'missing_alt_text': 'high',
        'image_missing_alt': 'high',
        'missing_form_labels': 'high',
        'keyboard_navigation_issues': 'medium',
        'poor_mobile_optimization': 'medium',
        
        # Image optimization
        'image_oversized': 'medium',
        'image_bad_filename': 'low',
        
        # Heading structure
        'title_too_short': 'medium',
        'title_too_long': 'medium',
        'meta_desc_too_short': 'medium',
        'meta_desc_too_long': 'medium',
        'h1_too_short': 'medium',
        'h1_too_long': 'medium',
        'multiple_h1': 'medium',
        'broken_heading_hierarchy': 'medium',
        'excessive_headings': 'low'
    }
    
    @classmethod
    def calculate_severity(cls, 
                          issue_type: str, 
                          context: Optional[Dict[str, Any]] = None) -> str:
        """
        Calculate standardized severity for an issue
        
        Args:
            issue_type: The type of SEO issue
            context: Additional context for severity escalation/de-escalation
        
        Returns:
            Severity level: 'critical', 'high', 'medium', or 'low'
        """
        base_severity = cls.BASE_SEVERITIES.get(issue_type, 'medium')
        context = context or {}
        
        # Apply context-based severity adjustments
        adjusted_severity = cls._apply_context_adjustments(issue_type, base_severity, context)
        
        return adjusted_severity
    
    @classmethod
    def _apply_context_adjustments(cls, 
                                  issue_type: str, 
                                  base_severity: str, 
                                  context: Dict[str, Any]) -> str:
        """Apply context-specific severity adjustments"""
        
        # JavaScript blocking severity based on location
        if issue_type == 'blocking_js_resource':
            in_head = context.get('in_head', False)
            if in_head:
                return cls._escalate_severity(base_severity)  # medium -> high
        
        # Resource issues based on file size or impact
        if issue_type in ['image_oversized', 'large_html']:
            size_mb = context.get('size_mb', 0)
            if size_mb > 2.0:  # Very large files
                return cls._escalate_severity(base_severity)
        
        # Performance issues based on estimated delay
        if issue_type in ['blocking_css_resource', 'blocking_js_resource']:
            estimated_delay = context.get('estimated_delay_ms', 0)
            if estimated_delay > 300:  # Significant delay
                return cls._escalate_severity(base_severity)
        
        # Content issues based on word count
        if issue_type == 'thin_content':
            word_count = context.get('word_count', 0)
            if word_count < 50:  # Extremely thin content
                return cls._escalate_severity(base_severity)  # medium -> high
        
        # Title/meta issues based on length extremes
        if issue_type in ['title_too_short', 'meta_desc_too_short']:
            length = context.get('length', 0)
            if length < 10:  # Extremely short
                return cls._escalate_severity(base_severity)
        
        # Site-wide frequency escalation (handled by deduplicator)
        frequency = context.get('site_wide_frequency', 1)
        if frequency > 15:  # Affects many pages
            return cls._escalate_severity(base_severity)
        
        return base_severity
    
    @classmethod
    def _escalate_severity(cls, current_severity: str) -> str:
        """Escalate severity by one level if possible"""
        severity_order = ['low', 'medium', 'high', 'critical']
        try:
            current_index = severity_order.index(current_severity)
            if current_index < len(severity_order) - 1:
                return severity_order[current_index + 1]
        except ValueError:
            logger.warning(f"Unknown severity level: {current_severity}")
        
        return current_severity
    
    @classmethod
    def _de_escalate_severity(cls, current_severity: str) -> str:
        """De-escalate severity by one level if possible"""
        severity_order = ['low', 'medium', 'high', 'critical']
        try:
            current_index = severity_order.index(current_severity)
            if current_index > 0:
                return severity_order[current_index - 1]
        except ValueError:
            logger.warning(f"Unknown severity level: {current_severity}")
        
        return current_severity
    
    @classmethod
    def get_severity_score(cls, severity: str) -> float:
        """Get numerical score for severity (for score impact calculations)"""
        severity_scores = {
            'critical': -10.0,
            'high': -6.0,
            'medium': -3.0,
            'low': -1.0
        }
        return severity_scores.get(severity, -3.0)
    
    @classmethod
    def validate_severity(cls, severity: str) -> str:
        """Validate and normalize severity values"""
        valid_severities = {'critical', 'high', 'medium', 'low'}
        if severity.lower() in valid_severities:
            return severity.lower()
        
        logger.warning(f"Invalid severity '{severity}', defaulting to 'medium'")
        return 'medium'