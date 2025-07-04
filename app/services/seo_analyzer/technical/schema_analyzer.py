"""
Schema Markup Analyzer
Analyzes Schema.org structured data for SEO
"""
from typing import Dict, List, Any, Optional
import logging
import re
import json
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class SchemaAnalyzer:
    """Analyzes Schema.org structured data"""
    
    def __init__(self):
        # Schema.org types commonly used for SEO
        self.important_schema_types = {
            'Organization', 'LocalBusiness', 'Person', 'Product', 'Service',
            'Article', 'BlogPosting', 'NewsArticle', 'Recipe', 'Event',
            'FAQ', 'HowTo', 'Review', 'AggregateRating', 'BreadcrumbList',
            'Website', 'WebPage', 'WebSite'
        }
    
    def analyze_schema_markup(self, crawl_result) -> Dict[str, Any]:
        """Analyze Schema.org structured data"""
        schema_data = {
            'has_schema': False,
            'schema_types': [],
            'schema_count': 0,
            'coverage_score': 0,
            'validation_errors': [],
            'recommendations': [],
            'raw_schemas': [],
            'page_type': 'unknown'
        }
        
        try:
            html_content = getattr(crawl_result, 'html', '')
            if not html_content:
                return schema_data
            
            # Extract JSON-LD schemas
            jsonld_schemas = self._extract_jsonld_schemas(html_content)
            
            # Extract Microdata schemas
            microdata_schemas = self._extract_microdata_schemas(html_content)
            
            # Extract RDFa schemas
            rdfa_schemas = self._extract_rdfa_schemas(html_content)
            
            all_schemas = jsonld_schemas + microdata_schemas + rdfa_schemas
            
            if all_schemas:
                schema_data['has_schema'] = True
                schema_data['schema_count'] = len(all_schemas)
                schema_data['raw_schemas'] = all_schemas
                
                # Extract schema types
                schema_types = self._extract_schema_types(all_schemas)
                schema_data['schema_types'] = schema_types
                
                # Validate schemas
                for schema in all_schemas:
                    validation = self._validate_schema_structure(schema)
                    if validation['errors']:
                        schema_data['validation_errors'].extend(validation['errors'])
                
                # Calculate coverage score
                schema_data['coverage_score'] = self._calculate_schema_coverage_score(schema_data)
                
                # Determine page type based on content
                schema_data['page_type'] = self._detect_page_content_type({'schema_data': schema_data})
                
                # Generate recommendations
                schema_data['recommendations'] = self._determine_recommended_schemas({'schema_data': schema_data})
            
        except Exception as e:
            logger.error(f"Error analyzing schema markup: {str(e)}")
            schema_data['validation_errors'].append(f"Analysis error: {str(e)}")
        
        return schema_data
    
    def _extract_jsonld_schemas(self, html_content: str) -> List[Dict[str, Any]]:
        """Extract JSON-LD structured data"""
        schemas = []
        
        # Find all JSON-LD script tags
        jsonld_pattern = r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>'
        matches = re.findall(jsonld_pattern, html_content, re.DOTALL | re.IGNORECASE)
        
        for match in matches:
            try:
                # Clean and parse JSON
                json_content = match.strip()
                schema_obj = json.loads(json_content)
                
                # Handle both single objects and arrays
                if isinstance(schema_obj, list):
                    schemas.extend(schema_obj)
                else:
                    schemas.append(schema_obj)
                    
            except json.JSONDecodeError as e:
                logger.warning(f"Invalid JSON-LD found: {str(e)}")
                continue
        
        return schemas
    
    def _extract_microdata_schemas(self, html_content: str) -> List[Dict[str, Any]]:
        """Extract Microdata structured data"""
        schemas = []
        
        # Find elements with itemscope
        itemscope_pattern = r'<[^>]*itemscope[^>]*itemtype=["\']([^"\']+)["\'][^>]*>'
        matches = re.findall(itemscope_pattern, html_content, re.IGNORECASE)
        
        for itemtype in matches:
            schema_type = itemtype.split('/')[-1]  # Get the type name
            schemas.append({
                '@type': schema_type,
                '@context': 'https://schema.org',
                'format': 'microdata'
            })
        
        return schemas
    
    def _extract_rdfa_schemas(self, html_content: str) -> List[Dict[str, Any]]:
        """Extract RDFa structured data"""
        schemas = []
        
        # Find elements with typeof attribute
        typeof_pattern = r'<[^>]*typeof=["\']([^"\']+)["\'][^>]*>'
        matches = re.findall(typeof_pattern, html_content, re.IGNORECASE)
        
        for typeof in matches:
            if 'schema.org' in typeof.lower():
                schema_type = typeof.split('/')[-1]  # Get the type name
                schemas.append({
                    '@type': schema_type,
                    '@context': 'https://schema.org',
                    'format': 'rdfa'
                })
        
        return schemas
    
    def _extract_schema_types(self, schema_json) -> List[str]:
        """Extract Schema types from structured data"""
        types = set()
        
        def extract_types_recursive(obj):
            if isinstance(obj, dict):
                if '@type' in obj:
                    schema_type = obj['@type']
                    if isinstance(schema_type, str):
                        types.add(schema_type)
                    elif isinstance(schema_type, list):
                        types.update(schema_type)
                
                # Recursively check nested objects
                for value in obj.values():
                    extract_types_recursive(value)
            elif isinstance(obj, list):
                for item in obj:
                    extract_types_recursive(item)
        
        if isinstance(schema_json, list):
            for schema in schema_json:
                extract_types_recursive(schema)
        else:
            extract_types_recursive(schema_json)
        
        return list(types)
    
    def _validate_schema_structure(self, schema_json) -> Dict[str, Any]:
        """Validate Schema.org structure"""
        validation = {
            'is_valid': True,
            'errors': [],
            'warnings': []
        }
        
        try:
            if isinstance(schema_json, dict):
                # Check for required @type
                if '@type' not in schema_json:
                    validation['errors'].append("Missing @type property")
                    validation['is_valid'] = False
                
                # Check for @context
                if '@context' not in schema_json:
                    validation['warnings'].append("Missing @context property")
                
                # Validate specific schema types
                schema_type = schema_json.get('@type', '')
                if schema_type == 'Organization':
                    if 'name' not in schema_json:
                        validation['errors'].append("Organization schema missing 'name' property")
                        validation['is_valid'] = False
                elif schema_type == 'Product':
                    required_props = ['name', 'description']
                    for prop in required_props:
                        if prop not in schema_json:
                            validation['errors'].append(f"Product schema missing '{prop}' property")
                            validation['is_valid'] = False
                
        except Exception as e:
            validation['errors'].append(f"Validation error: {str(e)}")
            validation['is_valid'] = False
        
        return validation
    
    def _calculate_schema_coverage_score(self, schema_data: Dict[str, Any]) -> float:
        """Calculate schema coverage score (0-100)"""
        if not schema_data['has_schema']:
            return 0.0
        
        score = 0.0
        
        # Base score for having schema
        score += 30.0
        
        # Points for important schema types
        important_types_found = set(schema_data['schema_types']) & self.important_schema_types
        score += min(len(important_types_found) * 10, 40)  # Max 40 points
        
        # Points for multiple schemas
        if schema_data['schema_count'] > 1:
            score += min(schema_data['schema_count'] * 2, 20)  # Max 20 points
        
        # Deduct points for validation errors
        error_penalty = min(len(schema_data['validation_errors']) * 5, 30)
        score -= error_penalty
        
        return max(0.0, min(100.0, score))
    
    def _detect_page_content_type(self, analysis: Dict[str, Any]) -> str:
        """Detect the main content type of the page"""
        schema_data = analysis.get('schema_data', {})
        schema_types = schema_data.get('schema_types', [])
        
        # Priority-based detection
        if any(t in schema_types for t in ['Product', 'Offer']):
            return 'product'
        elif any(t in schema_types for t in ['Article', 'BlogPosting', 'NewsArticle']):
            return 'article'
        elif any(t in schema_types for t in ['Organization', 'LocalBusiness']):
            return 'business'
        elif any(t in schema_types for t in ['Person']):
            return 'person'
        elif any(t in schema_types for t in ['Event']):
            return 'event'
        elif any(t in schema_types for t in ['Recipe']):
            return 'recipe'
        elif any(t in schema_types for t in ['FAQ', 'HowTo']):
            return 'informational'
        else:
            return 'general'
    
    def _determine_recommended_schemas(self, analysis: Dict[str, Any]) -> List[str]:
        """Determine recommended Schema types based on page content"""
        recommendations = []
        schema_data = analysis.get('schema_data', {})
        existing_types = set(schema_data.get('schema_types', []))
        page_type = schema_data.get('page_type', 'general')
        
        # Basic recommendations for all pages
        basic_schemas = {'WebPage', 'BreadcrumbList'}
        for schema in basic_schemas:
            if schema not in existing_types:
                recommendations.append(schema)
        
        # Content-type specific recommendations
        if page_type == 'product' and 'Product' not in existing_types:
            recommendations.extend(['Product', 'AggregateRating'])
        elif page_type == 'article' and 'Article' not in existing_types:
            recommendations.extend(['Article', 'Person'])  # Author
        elif page_type == 'business' and 'Organization' not in existing_types:
            recommendations.extend(['Organization', 'LocalBusiness'])
        elif page_type == 'general':
            # General page recommendations
            if 'Organization' not in existing_types:
                recommendations.append('Organization')
        
        return recommendations[:5]  # Limit to top 5 recommendations