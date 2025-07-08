"""
Issue Management Template Router
Provides the administrative interface for managing the SEO issue registry
"""

from fastapi import Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Dict, List, Any
import os
import logging

from app.core.issue_registry import IssueRegistry, IssueCategory, IssueSeverity, IssueFormat

logger = logging.getLogger(__name__)

# Template configuration
template_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "templates")
templates = Jinja2Templates(directory=template_dir)


async def issue_management_handler(request: Request) -> HTMLResponse:
    """
    Issue Management page handler - provides administrative interface for the issue registry
    """
    
    try:
        # Get all issues from registry
        all_issues = IssueRegistry.get_all_issues()
        
        # Organize issues by category for better display
        issues_by_category = {}
        for issue_type, issue_def in all_issues.items():
            category = issue_def.category.value
            if category not in issues_by_category:
                issues_by_category[category] = []
            
            issues_by_category[category].append({
                'issue_type': issue_type,
                'name_it': issue_def.name_it,
                'description_it': issue_def.description_it,
                'severity': issue_def.severity.value,
                'format_type': issue_def.format_type.value,
                'icon': issue_def.icon,
                'recommendations': issue_def.recommendations,
                'recommendation_count': len(issue_def.recommendations)
            })
        
        # Sort issues within each category by severity (critical first) then by name
        severity_order = {'critical': 1, 'high': 2, 'medium': 3, 'low': 4}
        for category in issues_by_category:
            issues_by_category[category].sort(key=lambda x: (
                severity_order.get(x['severity'], 5),
                x['name_it']
            ))
        
        # Calculate statistics
        total_issues = len(all_issues)
        
        category_stats = {}
        severity_stats = {}
        format_stats = {}
        
        for issue_def in all_issues.values():
            # Category stats
            category = issue_def.category.value
            category_stats[category] = category_stats.get(category, 0) + 1
            
            # Severity stats
            severity = issue_def.severity.value
            severity_stats[severity] = severity_stats.get(severity, 0) + 1
            
            # Format stats
            format_type = issue_def.format_type.value
            format_stats[format_type] = format_stats.get(format_type, 0) + 1
        
        # Prepare metadata for form dropdowns
        categories = [
            {'value': cat.value, 'label': cat.value.replace('_', ' ').title(), 'count': category_stats.get(cat.value, 0)}
            for cat in IssueCategory
        ]
        
        severities = [
            {
                'value': sev.value, 
                'label': sev.value.title(), 
                'count': severity_stats.get(sev.value, 0),
                'points': get_severity_points(sev.value)
            }
            for sev in IssueSeverity
        ]
        
        formats = [
            {'value': fmt.value, 'label': fmt.value.title(), 'count': format_stats.get(fmt.value, 0)}
            for fmt in IssueFormat
        ]
        
        # Build context for template
        context = {
            "request": request,
            "page_title": "Gestione Issue Registry - SEOAudit",
            "app_version": "2.0.0",
            "template_mode": True,
            "current_section": "issue_management",
            
            # Registry data
            "issues_by_category": issues_by_category,
            "total_issues": total_issues,
            
            # Statistics
            "category_stats": category_stats,
            "severity_stats": severity_stats,
            "format_stats": format_stats,
            
            # Metadata for forms
            "categories": categories,
            "severities": severities,
            "formats": formats,
            
            # UI helpers
            "severity_colors": {
                'critical': 'danger',
                'high': 'warning',
                'medium': 'info',
                'low': 'secondary'
            },
            "category_icons": {
                'technical_seo': 'bi-gear',
                'on_page': 'bi-file-text',
                'content': 'bi-card-text',
                'accessibility': 'bi-universal-access',
                'performance': 'bi-speedometer2',
                'mobile': 'bi-phone',
                'social': 'bi-share',
                'security': 'bi-shield-check'
            },
            "format_icons": {
                'granular': 'bi-zoom-in',
                'legacy': 'bi-archive',
                'consolidated': 'bi-collection'
            }
        }
        
        return templates.TemplateResponse("issue_management_wrapper.html", context)
        
    except Exception as e:
        logger.error(f"Error in issue_management handler: {str(e)}")
        logger.exception("Full traceback:")
        
        # Fallback context for error cases
        context = {
            "request": request,
            "page_title": "Errore - Gestione Issue Registry",
            "app_version": "2.0.0",
            "template_mode": True,
            "error_message": f"Errore nel caricamento del registry: {str(e)}",
            "current_section": "issue_management"
        }
        
        return templates.TemplateResponse("error.html", context)


def get_severity_points(severity: str) -> float:
    """Get the point impact for a severity level"""
    points_map = {
        'critical': -25.0,
        'high': -15.0,
        'medium': -8.0,
        'low': -3.0
    }
    return points_map.get(severity, 0.0)