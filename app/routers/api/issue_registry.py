"""
API Router for Issue Registry Management
Provides CRUD operations for the centralized issue registry
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum

from app.core.issue_registry import IssueRegistry, IssueCategory, IssueSeverity, IssueFormat, IssueDefinition

router = APIRouter(prefix="/api/v1/issue-registry", tags=["Issue Registry"])


class IssueCategoryEnum(str, Enum):
    TECHNICAL_SEO = "technical_seo"
    ON_PAGE = "on_page"
    CONTENT = "content"
    ACCESSIBILITY = "accessibility"
    PERFORMANCE = "performance"
    MOBILE = "mobile"
    SOCIAL = "social"
    SECURITY = "security"


class IssueSeverityEnum(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class IssueFormatEnum(str, Enum):
    GRANULAR = "granular"
    LEGACY = "legacy"
    CONSOLIDATED = "consolidated"


class IssueDefinitionResponse(BaseModel):
    """Response model for issue definition"""
    issue_type: str
    name_it: str
    description_it: str
    category: IssueCategoryEnum
    severity: IssueSeverityEnum
    format_type: IssueFormatEnum
    icon: str
    recommendations: List[str]
    escalation_rules: Optional[Dict[str, Any]] = None


class IssueDefinitionUpdate(BaseModel):
    """Model for updating issue definition"""
    name_it: Optional[str] = None
    description_it: Optional[str] = None
    category: Optional[IssueCategoryEnum] = None
    severity: Optional[IssueSeverityEnum] = None
    format_type: Optional[IssueFormatEnum] = None
    icon: Optional[str] = None
    recommendations: Optional[List[str]] = None
    escalation_rules: Optional[Dict[str, Any]] = None


class IssueDefinitionCreate(BaseModel):
    """Model for creating new issue definition"""
    issue_type: str = Field(..., min_length=1)
    name_it: str = Field(..., min_length=1)
    description_it: str = Field(..., min_length=1)
    category: IssueCategoryEnum
    severity: IssueSeverityEnum
    format_type: IssueFormatEnum = IssueFormatEnum.GRANULAR
    icon: str = "bi-exclamation-triangle"
    recommendations: List[str] = []
    escalation_rules: Dict[str, Any] = {}


@router.get("/", response_model=List[IssueDefinitionResponse])
async def get_all_issues():
    """Get all issue definitions from the registry"""
    try:
        all_issues = IssueRegistry.get_all_issues()
        return [
            IssueDefinitionResponse(
                issue_type=issue_type,
                name_it=issue_def.name_it,
                description_it=issue_def.description_it,
                category=issue_def.category.value,
                severity=issue_def.severity.value,
                format_type=issue_def.format_type.value,
                icon=issue_def.icon,
                recommendations=issue_def.recommendations,
                escalation_rules=getattr(issue_def, 'escalation_rules', None)
            )
            for issue_type, issue_def in all_issues.items()
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving issues: {str(e)}")


@router.get("/categories", response_model=List[Dict[str, str]])
async def get_categories():
    """Get all available issue categories"""
    return [
        {"value": category.value, "label": category.value.replace("_", " ").title()}
        for category in IssueCategory
    ]


@router.get("/severities", response_model=List[Dict[str, str]])
async def get_severities():
    """Get all available issue severities with their point values"""
    severity_points = {
        "critical": -25.0,
        "high": -15.0,
        "medium": -8.0,
        "low": -3.0
    }
    
    return [
        {
            "value": severity.value,
            "label": severity.value.title(),
            "points": severity_points.get(severity.value, 0.0)
        }
        for severity in IssueSeverity
    ]


@router.get("/formats", response_model=List[Dict[str, str]])
async def get_formats():
    """Get all available issue formats"""
    return [
        {"value": format_type.value, "label": format_type.value.title()}
        for format_type in IssueFormat
    ]


@router.get("/by-category/{category}", response_model=List[IssueDefinitionResponse])
async def get_issues_by_category(category: IssueCategoryEnum):
    """Get all issues in a specific category"""
    try:
        issues = IssueRegistry.get_issues_by_category(IssueCategory(category))
        return [
            IssueDefinitionResponse(
                issue_type=issue_type,
                name_it=issue_def.name_it,
                description_it=issue_def.description_it,
                category=issue_def.category.value,
                severity=issue_def.severity.value,
                format_type=issue_def.format_type.value,
                icon=issue_def.icon,
                recommendations=issue_def.recommendations,
                escalation_rules=getattr(issue_def, 'escalation_rules', None)
            )
            for issue_type, issue_def in issues.items()
        ]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid category: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving issues: {str(e)}")


@router.get("/by-severity/{severity}", response_model=List[IssueDefinitionResponse])
async def get_issues_by_severity(severity: IssueSeverityEnum):
    """Get all issues with a specific severity"""
    try:
        issues = IssueRegistry.get_issues_by_severity(IssueSeverity(severity))
        return [
            IssueDefinitionResponse(
                issue_type=issue_type,
                name_it=issue_def.name_it,
                description_it=issue_def.description_it,
                category=issue_def.category.value,
                severity=issue_def.severity.value,
                format_type=issue_def.format_type.value,
                icon=issue_def.icon,
                recommendations=issue_def.recommendations,
                escalation_rules=getattr(issue_def, 'escalation_rules', None)
            )
            for issue_type, issue_def in issues.items()
        ]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid severity: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving issues: {str(e)}")


@router.get("/{issue_type}", response_model=IssueDefinitionResponse)
async def get_issue(issue_type: str):
    """Get a specific issue definition"""
    try:
        issue_def = IssueRegistry.get_issue(issue_type)
        if not issue_def:
            raise HTTPException(status_code=404, detail=f"Issue type '{issue_type}' not found")
        
        return IssueDefinitionResponse(
            issue_type=issue_type,
            name_it=issue_def.name_it,
            description_it=issue_def.description_it,
            category=issue_def.category.value,
            severity=issue_def.severity.value,
            format_type=issue_def.format_type.value,
            icon=issue_def.icon,
            recommendations=issue_def.recommendations,
            escalation_rules=getattr(issue_def, 'escalation_rules', {})
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving issue: {str(e)}")


@router.get("/stats/summary")
async def get_registry_stats():
    """Get statistics about the issue registry"""
    try:
        all_issues = IssueRegistry.get_all_issues()
        
        # Count by category
        category_counts = {}
        severity_counts = {}
        format_counts = {}
        
        for issue_def in all_issues.values():
            # Category counts
            category = issue_def.category.value
            category_counts[category] = category_counts.get(category, 0) + 1
            
            # Severity counts
            severity = issue_def.severity.value
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            # Format counts
            format_type = issue_def.format_type.value
            format_counts[format_type] = format_counts.get(format_type, 0) + 1
        
        return {
            "total_issues": len(all_issues),
            "by_category": category_counts,
            "by_severity": severity_counts,
            "by_format": format_counts,
            "granular_percentage": round((format_counts.get("granular", 0) / len(all_issues)) * 100, 1)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating stats: {str(e)}")


# Note: POST, PUT, DELETE endpoints would require persistence layer
# For now, the registry is read-only from the static definition
# Future enhancement: add database persistence for dynamic issue management