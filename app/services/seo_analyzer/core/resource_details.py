"""
Resource Details Schema and Utilities
Structured data format for granular issue reporting
"""
import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from enum import Enum

class ResourceType(Enum):
    """Types of resources that can have SEO issues"""
    IMAGE = "image"
    CSS = "css" 
    JAVASCRIPT = "javascript"
    LINK = "link"
    META_TAG = "meta_tag"
    HEADING = "heading"
    CONTENT_BLOCK = "content_block"
    FORM_ELEMENT = "form_element"
    SCHEMA_MARKUP = "schema_markup"

@dataclass
class ResourceDetails:
    """Structured resource details for granular issue reporting"""
    resource_url: str
    resource_type: ResourceType
    issue_specific_data: Dict[str, Any]
    page_context: Optional[str] = None
    line_number: Optional[int] = None
    element_selector: Optional[str] = None
    
    def to_json(self) -> str:
        """Convert to JSON string for database storage"""
        data = asdict(self)
        data['resource_type'] = self.resource_type.value
        return json.dumps(data, ensure_ascii=False)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'ResourceDetails':
        """Create from JSON string"""
        data = json.loads(json_str)
        data['resource_type'] = ResourceType(data['resource_type'])
        return cls(**data)

class ResourceDetailsBuilder:
    """Builder for creating ResourceDetails objects"""
    
    @staticmethod
    def image_missing_alt(img_src: str, page_context: str = None, 
                         current_alt: str = "", selector: str = None) -> ResourceDetails:
        """Build details for image missing alt text"""
        return ResourceDetails(
            resource_url=img_src,
            resource_type=ResourceType.IMAGE,
            issue_specific_data={
                "current_alt": current_alt,
                "alt_length": len(current_alt) if current_alt else 0,
                "issue_type": "missing_alt" if not current_alt else "empty_alt"
            },
            page_context=page_context,
            element_selector=selector
        )
    
    @staticmethod 
    def image_oversized(img_src: str, width: int, height: int, 
                       file_size: Optional[int] = None, page_context: str = None) -> ResourceDetails:
        """Build details for oversized image"""
        return ResourceDetails(
            resource_url=img_src,
            resource_type=ResourceType.IMAGE,
            issue_specific_data={
                "current_width": width,
                "current_height": height,
                "file_size_bytes": file_size,
                "recommended_width": min(width, 1920),
                "recommended_height": min(height, 1080),
                "size_reduction_potential": max(0, (width * height) - (1920 * 1080))
            },
            page_context=page_context
        )
    
    @staticmethod
    def image_bad_filename(img_src: str, suggested_filename: str = None,
                          page_context: str = None) -> ResourceDetails:
        """Build details for non-SEO friendly image filename"""
        filename = img_src.split('/')[-1]
        return ResourceDetails(
            resource_url=img_src,
            resource_type=ResourceType.IMAGE,
            issue_specific_data={
                "current_filename": filename,
                "suggested_filename": suggested_filename or f"descriptive-{filename}",
                "seo_score": 0,
                "issues": ["non_descriptive", "no_keywords"]
            },
            page_context=page_context
        )
    
    @staticmethod
    def blocking_css(css_url: str, load_priority: str = "high",
                    estimated_delay: float = 0.0) -> ResourceDetails:
        """Build details for render-blocking CSS"""
        return ResourceDetails(
            resource_url=css_url,
            resource_type=ResourceType.CSS,
            issue_specific_data={
                "blocking_type": "render_blocking",
                "load_priority": load_priority,
                "estimated_delay_ms": estimated_delay,
                "optimization_suggestions": [
                    "Add media query for non-critical CSS",
                    "Inline critical CSS", 
                    "Use preload for important resources"
                ]
            },
            page_context="Document head"
        )
    
    @staticmethod
    def blocking_javascript(js_url: str, has_async: bool = False, 
                           has_defer: bool = False, estimated_delay: float = 0.0) -> ResourceDetails:
        """Build details for blocking JavaScript"""
        return ResourceDetails(
            resource_url=js_url,
            resource_type=ResourceType.JAVASCRIPT,
            issue_specific_data={
                "blocking_type": "script_blocking",
                "has_async": has_async,
                "has_defer": has_defer,
                "estimated_delay_ms": estimated_delay,
                "optimization_suggestions": [
                    "Add async attribute for non-critical scripts",
                    "Add defer attribute for DOM-dependent scripts",
                    "Move script to end of body"
                ]
            },
            page_context="Document head" if not has_async and not has_defer else "Document body"
        )
    
    @staticmethod
    def missing_schema(schema_type: str, page_section: str,
                      recommended_properties: List[str] = None) -> ResourceDetails:
        """Build details for missing schema markup"""
        return ResourceDetails(
            resource_url=f"schema://{schema_type}",
            resource_type=ResourceType.SCHEMA_MARKUP,
            issue_specific_data={
                "schema_type": schema_type,
                "missing_properties": recommended_properties or [],
                "implementation_example": f'{{"@type": "{schema_type}", "@context": "https://schema.org"}}',
                "seo_impact": "reduced_rich_snippets"
            },
            page_context=page_section
        )
    
    @staticmethod
    def form_missing_label(input_id: str, input_type: str, input_name: str = "",
                          page_context: str = None) -> ResourceDetails:
        """Build details for form input missing label"""
        return ResourceDetails(
            resource_url=f"input#{input_id}" if input_id else f"input[name='{input_name}']",
            resource_type=ResourceType.FORM_ELEMENT,
            issue_specific_data={
                "input_type": input_type,
                "input_id": input_id,
                "input_name": input_name,
                "has_placeholder": False,  # To be filled by analyzer
                "accessibility_impact": "screen_reader_unusable",
                "suggested_label": f"Label for {input_name or input_type} field"
            },
            page_context=page_context,
            element_selector=f"input#{input_id}" if input_id else f"input[name='{input_name}']"
        )
    
    @staticmethod
    def content_thin(section_selector: str, word_count: int, 
                    min_expected: int = 500, content_type: str = "general") -> ResourceDetails:
        """Build details for thin content section"""
        return ResourceDetails(
            resource_url=f"content://{section_selector}",
            resource_type=ResourceType.CONTENT_BLOCK,
            issue_specific_data={
                "current_word_count": word_count,
                "minimum_recommended": min_expected,
                "content_type": content_type,
                "expansion_needed": min_expected - word_count,
                "quality_suggestions": [
                    "Add more detailed explanations",
                    "Include relevant examples",
                    "Expand on key points"
                ]
            },
            page_context=f"Content section: {section_selector}",
            element_selector=section_selector
        )

class IssueFactory:
    """Factory for creating granular issues with resource details"""
    
    @staticmethod
    def create_granular_issue(issue_type: str, severity: str, category: str,
                            title: str, description: str, recommendation: str,
                            resource_details: ResourceDetails, score_impact: float = 0.0) -> Dict[str, Any]:
        """Create a granular issue with structured resource details"""
        return {
            'type': issue_type,
            'severity': severity,
            'category': category,
            'title': title,
            'description': description,
            'recommendation': recommendation,
            'element': resource_details.to_json(),
            'score_impact': score_impact
        }
    
    @staticmethod
    def extract_resource_details(issue: Dict[str, Any]) -> Optional[ResourceDetails]:
        """Extract ResourceDetails from an issue's element field"""
        element_data = issue.get('element')
        if not element_data:
            return None
        
        try:
            # Try to parse as JSON (new format)
            return ResourceDetails.from_json(element_data)
        except (json.JSONDecodeError, KeyError):
            # Fallback for old format (plain text)
            return None
    
    @staticmethod
    def group_issues_by_resource_type(issues: List[Dict[str, Any]]) -> Dict[ResourceType, List[Dict[str, Any]]]:
        """Group issues by their resource type"""
        grouped = {}
        
        for issue in issues:
            resource_details = IssueFactory.extract_resource_details(issue)
            if resource_details:
                resource_type = resource_details.resource_type
                if resource_type not in grouped:
                    grouped[resource_type] = []
                grouped[resource_type].append(issue)
        
        return grouped