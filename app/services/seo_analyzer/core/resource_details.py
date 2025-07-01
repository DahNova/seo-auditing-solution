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
    CONSOLIDATED = "consolidated"

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
    def image_optimization_needed(img_src: str, width: int = None, height: int = None, 
                                 file_size: Optional[int] = None, alt_text: str = "", 
                                 lazy_loading: bool = False, format_type: str = "unknown",
                                 page_context: str = None) -> ResourceDetails:
        """Build details for image that needs optimization"""
        # Calculate optimization potential
        optimization_potential = []
        estimated_savings = 0
        
        if file_size and file_size > 500000:  # >500KB
            optimization_potential.append("compressione")
            estimated_savings += file_size * 0.6  # 60% potential savings
        
        if width and height and (width > 1920 or height > 1080):
            optimization_potential.append("ridimensionamento")
            estimated_savings += (width * height - 1920 * 1080) * 3  # bytes estimate
        
        if format_type.lower() in ['jpeg', 'jpg', 'png']:
            optimization_potential.append("formato_moderno")
            estimated_savings += file_size * 0.3 if file_size else 50000  # 30% savings with WebP
        
        if not lazy_loading:
            optimization_potential.append("lazy_loading")
        
        if not alt_text or len(alt_text) < 5:
            optimization_potential.append("alt_text")
        
        # Determine priority based on optimization potential
        priority = "high" if len(optimization_potential) >= 3 else "medium"
        
        return ResourceDetails(
            resource_url=img_src,
            resource_type=ResourceType.IMAGE,
            issue_specific_data={
                "current_width": width,
                "current_height": height,
                "file_size_bytes": file_size,
                "file_size_kb": round(file_size / 1024) if file_size else None,
                "current_format": format_type,
                "has_alt_text": bool(alt_text and len(alt_text) > 0),
                "alt_text_length": len(alt_text) if alt_text else 0,
                "has_lazy_loading": lazy_loading,
                "optimization_potential": optimization_potential,
                "estimated_savings_bytes": int(estimated_savings),
                "estimated_savings_kb": round(estimated_savings / 1024) if estimated_savings else 0,
                "recommended_width": min(width, 1920) if width else None,
                "recommended_height": min(height, 1080) if height else None,
                "recommended_format": "WebP" if format_type.lower() in ['jpeg', 'jpg', 'png'] else format_type
            },
            page_context=page_context,
            element_selector=f'img[src*="{img_src.split("/")[-1]}"]',
            optimization_suggestions=[
                "Comprimi l'immagine mantenendo la qualità visiva (80-85% qualità JPEG)",
                "Considera il formato WebP per riduzione del 25-35% delle dimensioni",
                "Aggiungi loading='lazy' per images below-the-fold",
                "Ridimensiona alle dimensioni massime necessarie (max 1920x1080 per desktop)",
                "Aggiungi alt text descrittivo per accessibilità e SEO" if not alt_text else None,
                "Usa responsive images con srcset per device optimization"
            ],
            priority_level=priority,
            estimated_fix_time="5-15 minutes"
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
    def poor_social_meta(page_url: str, missing_tags: List[str], present_tags: List[Dict[str, Any]] = None,
                        platform_coverage: Dict[str, float] = None, page_title: str = "", 
                        page_context: str = "") -> ResourceDetails:
        """Build details for poor social media meta tags with platform-specific suggestions"""
        present_tags = present_tags or []
        platform_coverage = platform_coverage or {}
        
        # Analyze which platforms need the most attention
        critical_platforms = []
        for platform, coverage in platform_coverage.items():
            if coverage < 50:
                critical_platforms.append(platform)
        
        # Generate platform-specific suggestions
        platform_suggestions = []
        
        # Facebook/Open Graph suggestions
        if 'facebook' in critical_platforms or any('og:' in tag for tag in missing_tags):
            platform_suggestions.extend([
                "Aggiungi Open Graph per Facebook: og:title, og:description, og:image",
                "Usa immagini 1200x630px per og:image per risultati ottimali",
                "Includi og:type per specificare il tipo di contenuto"
            ])
        
        # Twitter suggestions
        if 'twitter' in critical_platforms or any('twitter:' in tag for tag in missing_tags):
            platform_suggestions.extend([
                "Aggiungi Twitter Card: twitter:card, twitter:title, twitter:description",
                "Considera twitter:image per maggiore engagement",
                "Usa twitter:site per identificare l'account Twitter"
            ])
        
        # LinkedIn suggestions (uses Open Graph)
        if 'linkedin' in critical_platforms:
            platform_suggestions.append("LinkedIn utilizza Open Graph - ottimizza og: tags")
        
        # Generate optimal social meta implementation
        suggested_implementation = []
        if page_title:
            suggested_implementation.extend([
                f'<meta property="og:title" content="{page_title}">',
                f'<meta name="twitter:title" content="{page_title}">'
            ])
        
        return ResourceDetails(
            resource_url=page_url,
            resource_type=ResourceType.SOCIAL_META,
            issue_specific_data={
                "missing_tags": missing_tags,
                "present_tags": present_tags,
                "platform_coverage": platform_coverage,
                "critical_platforms": critical_platforms,
                "overall_social_score": sum(platform_coverage.values()) / len(platform_coverage) if platform_coverage else 0,
                "suggested_implementation": suggested_implementation,
                "social_seo_impact": "reduced_social_visibility_and_ctr"
            },
            page_context=page_context,
            element_selector="<head>",
            optimization_suggestions=[
                "Implementa meta tag Open Graph per condivisioni Facebook e LinkedIn",
                "Aggiungi Twitter Card meta tags per condivisioni Twitter ottimizzate",
                "Usa immagini specifiche per social (1200x630px) per massimizzare l'impatto",
                "Testa le condivisioni con Facebook Sharing Debugger e Twitter Card Validator"
            ] + platform_suggestions,
            priority_level="medium",
            estimated_fix_time="10-20 minutes"
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
    
    @staticmethod
    def canonical_missing(page_url: str, suggested_canonical: str, 
                         duplicate_count: int = 0, page_context: str = "") -> ResourceDetails:
        """Details for missing canonical URL issue"""
        return ResourceDetails(
            resource_url=page_url,
            resource_type=ResourceType.META_TAG,
            issue_specific_data={
                "current_canonical": None,
                "suggested_canonical": suggested_canonical,
                "duplicate_count": duplicate_count,
                "has_duplicates": duplicate_count > 1,
                "canonical_status": "missing"
            },
            page_context=page_context,
            element_selector="<head>",
            optimization_suggestions=[
                f"Aggiungi: <link rel=\"canonical\" href=\"{suggested_canonical}\">",
                "Posiziona il tag canonical nella sezione <head>",
                "Assicurati che l'URL canonical sia assoluto e accessibile"
            ],
            priority_level="high",
            estimated_fix_time="2-5 minutes"
        )
    
    @staticmethod
    def h1_missing(page_url: str, suggested_h1: str, title_text: str = "", 
                   top_keywords: List[str] = None, page_context: str = "") -> ResourceDetails:
        """Details for missing H1 tag issue"""
        keywords = top_keywords or []
        keyword_suggestions = []
        
        if keywords:
            keyword_suggestions = [
                f"Includi la keyword principale: '{keywords[0]}'",
                f"Considera keyword secondarie: {', '.join(keywords[1:3])}" if len(keywords) > 1 else ""
            ]
            keyword_suggestions = [s for s in keyword_suggestions if s]
        
        return ResourceDetails(
            resource_url=page_url,
            resource_type=ResourceType.HEADING,
            issue_specific_data={
                "current_h1": None,
                "suggested_h1": suggested_h1,
                "page_title": title_text,
                "top_keywords": keywords[:5],
                "h1_status": "missing",
                "seo_impact": "major_ranking_factor"
            },
            page_context=page_context,
            element_selector="<body>",
            optimization_suggestions=[
                f"Aggiungi H1 ottimizzato: <h1>{suggested_h1}</h1>",
                "Posiziona l'H1 nella parte alta del contenuto principale",
                "Mantieni l'H1 tra 10-70 caratteri per leggibilità ottimale",
                "Usa un solo H1 per pagina per chiarezza semantica"
            ] + keyword_suggestions,
            priority_level="high",
            estimated_fix_time="3-10 minutes"
        )
    
    @staticmethod
    def meta_description_missing(page_url: str, suggested_description: str, title_text: str = "", 
                                content_preview: str = "", top_keywords: List[str] = None, 
                                page_context: str = "") -> ResourceDetails:
        """Details for missing meta description issue"""
        keywords = top_keywords or []
        
        return ResourceDetails(
            resource_url=page_url,
            resource_type=ResourceType.META_TAG,
            issue_specific_data={
                "current_meta_description": None,
                "suggested_meta_description": suggested_description,
                "page_title": title_text,
                "content_preview": content_preview[:200],
                "top_keywords": keywords[:3],
                "meta_description_status": "missing",
                "optimal_length": "150-160 caratteri",
                "seo_impact": "affects_search_results_ctr"
            },
            page_context=page_context,
            element_selector='<head>',
            optimization_suggestions=[
                f"Aggiungi meta description: <meta name=\"description\" content=\"{suggested_description[:120]}...\">",
                "Mantieni la lunghezza tra 150-160 caratteri per visualizzazione ottimale",
                "Includi la keyword principale in modo naturale",
                "Scrivi una descrizione accattivante che inviti al click",
                "Evita duplicazioni con altre pagine del sito"
            ],
            priority_level="high",
            estimated_fix_time="5-15 minutes"
        )
    
    @staticmethod
    def viewport_missing(page_url: str, page_context: str = "", mobile_analysis: Dict[str, Any] = None) -> ResourceDetails:
        """Details for missing viewport meta tag issue"""
        mobile_data = mobile_analysis or {}
        current_viewport = mobile_data.get('viewport_content', '')
        
        # Determine optimal viewport based on page analysis
        optimal_viewport = "width=device-width, initial-scale=1.0"
        
        # Check for responsive indicators to suggest advanced viewport
        responsive_indicators = mobile_data.get('responsive_indicators', 0)
        if responsive_indicators >= 3:
            optimal_viewport = "width=device-width, initial-scale=1.0, viewport-fit=cover"
        
        return ResourceDetails(
            resource_url=page_url,
            resource_type=ResourceType.META_TAG,
            issue_specific_data={
                "current_viewport": current_viewport,
                "optimal_viewport": optimal_viewport,
                "mobile_score": mobile_data.get('mobile_score', 0),
                "responsive_indicators": responsive_indicators,
                "viewport_status": "missing" if not current_viewport else "suboptimal",
                "mobile_seo_impact": "major_mobile_ranking_penalty"
            },
            page_context=page_context,
            element_selector="<head>",
            optimization_suggestions=[
                f"Aggiungi viewport meta tag: <meta name=\"viewport\" content=\"{optimal_viewport}\">",
                "Posiziona il tag viewport nella sezione <head> prima di altri meta tag",
                "Testa la visualizzazione su dispositivi mobili dopo l'implementazione",
                "Considera viewport-fit=cover per siti con design edge-to-edge",
                "Verifica che il contenuto sia leggibile senza zoom su mobile"
            ],
            priority_level="high",
            estimated_fix_time="2-5 minutes"
        )
    
    @staticmethod
    def schema_markup_missing(page_url: str, recommended_schema_types: List[str], 
                             page_content_type: str = "general", business_type: str = "",
                             page_context: str = "") -> ResourceDetails:
        """Details for missing schema markup issue"""
        primary_schema = recommended_schema_types[0] if recommended_schema_types else "Organization"
        
        # Generate schema-specific suggestions based on content type
        schema_suggestions = []
        implementation_examples = {}
        
        if "Organization" in recommended_schema_types or "LocalBusiness" in recommended_schema_types:
            schema_suggestions.extend([
                "Aggiungi schema Organization per informazioni aziendali",
                "Includi nome, indirizzo, telefono e sito web",
                "Considera LocalBusiness se hai una sede fisica"
            ])
            implementation_examples["Organization"] = {
                "@type": "Organization",
                "name": "Nome Azienda",
                "url": page_url,
                "address": {"@type": "PostalAddress"},
                "contactPoint": {"@type": "ContactPoint"}
            }
        
        if "Product" in recommended_schema_types:
            schema_suggestions.extend([
                "Aggiungi schema Product per prodotti/servizi",
                "Includi nome, descrizione, prezzo e disponibilità",
                "Aggiungi recensioni e valutazioni se disponibili"
            ])
            implementation_examples["Product"] = {
                "@type": "Product",
                "name": "Nome Prodotto",
                "description": "Descrizione prodotto",
                "offers": {"@type": "Offer"}
            }
        
        if "Article" in recommended_schema_types or "BlogPosting" in recommended_schema_types:
            schema_suggestions.extend([
                "Aggiungi schema Article per contenuti informativi",
                "Includi autore, data pubblicazione e immagine",
                "Considera NewsArticle per notizie specifiche"
            ])
            implementation_examples["Article"] = {
                "@type": "Article",
                "headline": "Titolo Articolo",
                "author": {"@type": "Person", "name": "Nome Autore"},
                "datePublished": "2024-01-01"
            }
        
        if "BreadcrumbList" in recommended_schema_types:
            schema_suggestions.append("Aggiungi schema BreadcrumbList per la navigazione")
            implementation_examples["BreadcrumbList"] = {
                "@type": "BreadcrumbList",
                "itemListElement": [{"@type": "ListItem", "position": 1}]
            }
        
        return ResourceDetails(
            resource_url=page_url,
            resource_type=ResourceType.SCHEMA_MARKUP,
            issue_specific_data={
                "missing_schema_types": recommended_schema_types,
                "primary_recommended": primary_schema,
                "page_content_type": page_content_type,
                "business_type": business_type,
                "implementation_examples": implementation_examples,
                "schema_impact": "reduced_rich_snippets_and_visibility",
                "priority_schemas": recommended_schema_types[:3]
            },
            page_context=page_context,
            element_selector="<head>",
            optimization_suggestions=[
                f"Implementa schema {primary_schema} come priorità principale",
                "Posiziona il JSON-LD nella sezione <head> della pagina",
                "Testa l'implementazione con Google Rich Results Test",
                "Includi tutte le proprietà richieste per rich snippets"
            ] + schema_suggestions,
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
    def create_consolidated_issue(issue_type: str, severity: str, category: str,
                                title: str, description: str, recommendation: str,
                                resources_details: List[ResourceDetails], score_impact: float = 0.0) -> Dict[str, Any]:
        """Create a consolidated issue with multiple resource details"""
        # Create a consolidated element with all resources
        consolidated_element = {
            'resource_type': 'consolidated',
            'resources': [details.to_json() for details in resources_details],
            'total_count': len(resources_details)
        }
        
        return {
            'type': issue_type,
            'severity': severity,
            'category': category,
            'title': title,
            'description': description,
            'recommendation': recommendation,
            'element': json.dumps(consolidated_element, ensure_ascii=False),
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
    def extract_consolidated_resources(issue: Dict[str, Any]) -> Optional[List[ResourceDetails]]:
        """Extract ResourceDetails list from a consolidated issue's element field"""
        element_data = issue.get('element')
        if not element_data:
            return None
        
        try:
            # Parse as JSON
            data = json.loads(element_data)
            if data.get('resource_type') == 'consolidated':
                resources = []
                for resource_json in data.get('resources', []):
                    # Parse each individual resource
                    resource_data = json.loads(resource_json)
                    # Convert resource_type string back to enum
                    resource_data['resource_type'] = ResourceType(resource_data['resource_type'])
                    resources.append(ResourceDetails(**resource_data))
                return resources
            else:
                # Single resource format - try to extract as normal ResourceDetails
                try:
                    single_resource = ResourceDetails.from_json(element_data)
                    return [single_resource] if single_resource else None
                except (ValueError, KeyError):
                    # If it fails, it might be an old format - return None
                    return None
        except (json.JSONDecodeError, KeyError, ValueError):
            # Fallback for old format
            return None
    
    @staticmethod
    def is_consolidated_issue(issue: Dict[str, Any]) -> bool:
        """Check if an issue is a consolidated issue with multiple resources"""
        element_data = issue.get('element')
        if not element_data:
            return False
        
        try:
            data = json.loads(element_data)
            return data.get('resource_type') == 'consolidated'
        except (json.JSONDecodeError, KeyError):
            return False
    
    @staticmethod
    def group_issues_by_resource_type(issues: List[Dict[str, Any]]) -> Dict[ResourceType, List[Dict[str, Any]]]:
        """Group issues by their resource type"""
        grouped = {}
        
        for issue in issues:
            # Check if it's a consolidated issue first
            if IssueFactory.is_consolidated_issue(issue):
                # For consolidated issues, get the first resource type
                consolidated_resources = IssueFactory.extract_consolidated_resources(issue)
                if consolidated_resources and len(consolidated_resources) > 0:
                    resource_type = consolidated_resources[0].resource_type
                    if resource_type not in grouped:
                        grouped[resource_type] = []
                    grouped[resource_type].append(issue)
            else:
                # Single resource issue
                resource_details = IssueFactory.extract_resource_details(issue)
                if resource_details:
                    resource_type = resource_details.resource_type
                    if resource_type not in grouped:
                        grouped[resource_type] = []
                    grouped[resource_type].append(issue)
        
        return grouped