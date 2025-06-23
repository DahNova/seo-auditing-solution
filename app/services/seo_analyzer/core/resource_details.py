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
    URL_STRUCTURE = "url_structure"
    SOCIAL_META = "social_meta"
    ACCESSIBILITY = "accessibility"

@dataclass
class ResourceDetails:
    """Structured resource details for granular issue reporting"""
    resource_url: str
    resource_type: ResourceType
    issue_specific_data: Dict[str, Any]
    page_context: Optional[str] = None
    line_number: Optional[int] = None
    element_selector: Optional[str] = None
    optimization_suggestions: Optional[List[str]] = None
    priority_level: Optional[str] = None  # 'critical', 'high', 'medium', 'low'
    estimated_fix_time: Optional[str] = None  # e.g., "5 minutes", "30 minutes", "2 hours"
    
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
            element_selector=selector,
            optimization_suggestions=[
                "Add descriptive alt text that explains what the image shows",
                "Include relevant keywords naturally in alt text",
                "Keep alt text under 125 characters for screen readers",
                "Use empty alt='' for decorative images only"
            ],
            priority_level="high",
            estimated_fix_time="2-5 minutes"
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
            },
            page_context="Document head",
            optimization_suggestions=[
                "Add media query for non-critical CSS",
                "Inline critical CSS above-the-fold", 
                "Use preload with onload for non-critical CSS",
                "Minify and compress CSS files"
            ],
            priority_level="high",
            estimated_fix_time="15-30 minutes"
        )
    
    @staticmethod
    def blocking_javascript(js_url: str, has_async: bool = False, 
                           has_defer: bool = False, estimated_delay: float = 0.0) -> ResourceDetails:
        """Build details for blocking JavaScript"""
        priority = "high" if estimated_delay > 200 else "medium"
        fix_time = "5-10 minutes" if "analytics" in js_url.lower() else "10-20 minutes"
        
        return ResourceDetails(
            resource_url=js_url,
            resource_type=ResourceType.JAVASCRIPT,
            issue_specific_data={
                "blocking_type": "script_blocking",
                "has_async": has_async,
                "has_defer": has_defer,
                "estimated_delay_ms": estimated_delay,
            },
            page_context="Document head" if not has_async and not has_defer else "Document body",
            optimization_suggestions=[
                "Add async attribute for non-critical scripts (analytics, tracking)",
                "Add defer attribute for DOM-dependent scripts",
                "Move non-critical scripts to end of body",
                "Consider loading third-party scripts on user interaction"
            ],
            priority_level=priority,
            estimated_fix_time=fix_time
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
    
    @staticmethod
    def poor_social_meta(missing_tags: List[str], page_url: str) -> ResourceDetails:
        """Build details for poor social media meta tags"""
        return ResourceDetails(
            resource_url=page_url,
            resource_type=ResourceType.SOCIAL_META,
            issue_specific_data={
                "missing_tags": missing_tags,
                "impact": "poor_social_sharing",
                "platforms_affected": ["Facebook", "Twitter", "LinkedIn"]
            },
            page_context="Document head",
            optimization_suggestions=[
                "Add Open Graph (og:) tags for Facebook sharing",
                "Add Twitter Card meta tags",
                "Include og:image with proper dimensions (1200x630px)",
                "Add og:title and og:description different from page title/meta"
            ],
            priority_level="medium",
            estimated_fix_time="10-15 minutes"
        )
    
    @staticmethod
    def url_structure_issue(url: str, issue_details: Dict[str, Any]) -> ResourceDetails:
        """Build details for URL structure problems"""
        return ResourceDetails(
            resource_url=url,
            resource_type=ResourceType.URL_STRUCTURE,
            issue_specific_data={
                "issues": issue_details.get("issues", []),
                "url_length": len(url),
                "has_parameters": "?" in url,
                "readability_score": issue_details.get("readability_score", 0)
            },
            page_context="URL structure",
            optimization_suggestions=[
                "Use descriptive, keyword-rich URLs",
                "Remove unnecessary parameters",
                "Use hyphens instead of underscores",
                "Keep URLs under 100 characters when possible"
            ],
            priority_level="medium",
            estimated_fix_time="30-60 minutes"
        )
    
    @staticmethod
    def missing_schema_markup(schema_type: str, page_context: str = None) -> ResourceDetails:
        """Build details for missing schema markup"""
        return ResourceDetails(
            resource_url=f"schema://{schema_type}",
            resource_type=ResourceType.SCHEMA_MARKUP,
            issue_specific_data={
                "recommended_schema": schema_type,
                "seo_impact": "reduced_rich_snippets",
                "implementation_priority": "high" if schema_type in ["Organization", "LocalBusiness"] else "medium"
            },
            page_context=page_context or "Page content",
            optimization_suggestions=[
                f"Add {schema_type} JSON-LD schema markup",
                "Include required properties for rich snippets",
                "Test implementation with Google's Rich Results Test",
                "Consider additional schema types for enhanced visibility"
            ],
            priority_level="medium",
            estimated_fix_time="20-45 minutes"
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