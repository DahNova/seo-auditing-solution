"""
Advanced Technical SEO Analyzer
Analyzes Schema markup, Social meta tags, and technical SEO factors
"""
from typing import Dict, List, Any, Optional
import logging
import re
import json
from urllib.parse import urlparse, urljoin

logger = logging.getLogger(__name__)

class TechnicalSEOAnalyzer:
    """Advanced technical SEO analysis including Schema, Social tags, and more"""
    
    def __init__(self):
        # Schema.org types commonly used for SEO
        self.important_schema_types = {
            'Organization', 'LocalBusiness', 'Person', 'Product', 'Service',
            'Article', 'BlogPosting', 'NewsArticle', 'Recipe', 'Event',
            'FAQ', 'HowTo', 'Review', 'AggregateRating', 'BreadcrumbList',
            'Website', 'WebPage', 'WebSite'
        }
        
        # Social media platforms and their meta tags
        self.social_platforms = {
            'facebook': {
                'prefix': 'og:',
                'required': ['og:title', 'og:description', 'og:image', 'og:url', 'og:type'],
                'recommended': ['og:site_name', 'og:locale', 'fb:app_id']
            },
            'twitter': {
                'prefix': 'twitter:',
                'required': ['twitter:card', 'twitter:title', 'twitter:description'],
                'recommended': ['twitter:image', 'twitter:site', 'twitter:creator']
            },
            'linkedin': {
                'prefix': 'og:',  # LinkedIn uses Open Graph
                'required': ['og:title', 'og:description', 'og:image', 'og:url'],
                'recommended': ['og:type', 'og:site_name']
            }
        }
        
        # Technical SEO factors
        self.technical_factors = {
            'canonical_url': {'importance': 'high'},
            'robots_meta': {'importance': 'high'},
            'viewport_meta': {'importance': 'high'},
            'charset_meta': {'importance': 'medium'},
            'lang_attribute': {'importance': 'medium'},
            'hreflang': {'importance': 'medium'},
            'sitemap_reference': {'importance': 'medium'},
            'robots_txt_reference': {'importance': 'low'}
        }
    
    def analyze_technical_seo(self, crawl_result, domain: str) -> Dict[str, Any]:
        """Comprehensive technical SEO analysis"""
        analysis = {
            'schema_markup': self.analyze_schema_markup(crawl_result),
            'social_meta_tags': self.analyze_social_meta_tags(crawl_result),
            'technical_tags': self.analyze_technical_tags(crawl_result, domain),
            'robots_analysis': self.analyze_robots_directives(crawl_result),
            'mobile_optimization': self.analyze_mobile_optimization(crawl_result),
            'internationalization': self.analyze_internationalization(crawl_result),
            'technical_issues': [],
            'technical_opportunities': []
        }
        
        # Generate issues and opportunities based on analysis
        analysis['technical_issues'] = self._identify_technical_issues(analysis)
        analysis['technical_opportunities'] = self._generate_technical_opportunities(analysis)
        
        return analysis
    
    def analyze_schema_markup(self, crawl_result) -> Dict[str, Any]:
        """Analyze structured data (Schema.org) markup"""
        schema_data = {
            'has_schema': False,
            'schema_types': [],
            'json_ld_count': 0,
            'microdata_count': 0,
            'rdfa_count': 0,
            'valid_schemas': [],
            'schema_errors': [],
            'coverage_score': 0
        }
        
        try:
            html_content = getattr(crawl_result, 'html', '')
            if not html_content:
                return schema_data
            
            # JSON-LD detection and parsing
            json_ld_scripts = re.findall(
                r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
                html_content, re.DOTALL | re.IGNORECASE
            )
            
            schema_data['json_ld_count'] = len(json_ld_scripts)
            
            for script_content in json_ld_scripts:
                try:
                    # Clean and parse JSON-LD
                    cleaned_content = script_content.strip()
                    schema_json = json.loads(cleaned_content)
                    
                    # Extract schema types
                    schema_types = self._extract_schema_types(schema_json)
                    schema_data['schema_types'].extend(schema_types)
                    
                    # Validate common schemas
                    validation = self._validate_schema_structure(schema_json)
                    if validation['valid']:
                        schema_data['valid_schemas'].append(validation)
                    else:
                        schema_data['schema_errors'].extend(validation['errors'])
                        
                except json.JSONDecodeError as e:
                    schema_data['schema_errors'].append(f"Invalid JSON-LD: {str(e)}")
                except Exception as e:
                    logger.error(f"Error parsing schema: {str(e)}")
            
            # Microdata detection
            microdata_items = re.findall(r'itemtype=["\']([^"\']*)["\']', html_content, re.IGNORECASE)
            schema_data['microdata_count'] = len(microdata_items)
            
            # RDFa detection  
            rdfa_items = re.findall(r'typeof=["\']([^"\']*)["\']', html_content, re.IGNORECASE)
            schema_data['rdfa_count'] = len(rdfa_items)
            
            # Overall schema presence
            schema_data['has_schema'] = (
                schema_data['json_ld_count'] > 0 or 
                schema_data['microdata_count'] > 0 or 
                schema_data['rdfa_count'] > 0
            )
            
            # Calculate coverage score
            schema_data['coverage_score'] = self._calculate_schema_coverage_score(schema_data)
            
        except Exception as e:
            logger.error(f"Error analyzing schema markup: {str(e)}")
            
        return schema_data
    
    def analyze_social_meta_tags(self, crawl_result) -> Dict[str, Any]:
        """Analyze social media meta tags (Open Graph, Twitter Cards, etc.)"""
        social_data = {
            'platforms': {},
            'overall_coverage': 0,
            'missing_tags': [],
            'social_score': 0
        }
        
        try:
            html_content = getattr(crawl_result, 'html', '')
            if not html_content:
                return social_data
            
            # Extract all meta tags
            meta_tags = re.findall(
                r'<meta[^>]*(?:property|name)=["\']([^"\']*)["\'][^>]*content=["\']([^"\']*)["\'][^>]*>',
                html_content, re.IGNORECASE
            )
            
            meta_dict = {tag[0].lower(): tag[1] for tag in meta_tags}
            
            # Analyze each platform
            for platform, config in self.social_platforms.items():
                platform_data = {
                    'present_tags': [],
                    'missing_required': [],
                    'missing_recommended': [],
                    'coverage_score': 0
                }
                
                # Check required tags
                for required_tag in config['required']:
                    if required_tag.lower() in meta_dict:
                        platform_data['present_tags'].append({
                            'tag': required_tag,
                            'content': meta_dict[required_tag.lower()],
                            'type': 'required'
                        })
                    else:
                        platform_data['missing_required'].append(required_tag)
                
                # Check recommended tags
                for recommended_tag in config['recommended']:
                    if recommended_tag.lower() in meta_dict:
                        platform_data['present_tags'].append({
                            'tag': recommended_tag,
                            'content': meta_dict[recommended_tag.lower()],
                            'type': 'recommended'
                        })
                    else:
                        platform_data['missing_recommended'].append(recommended_tag)
                
                # Calculate platform coverage score
                required_present = len(config['required']) - len(platform_data['missing_required'])
                recommended_present = len(config['recommended']) - len(platform_data['missing_recommended'])
                
                # Weight required tags more heavily
                total_possible = len(config['required']) * 2 + len(config['recommended'])
                total_score = required_present * 2 + recommended_present
                platform_data['coverage_score'] = (total_score / total_possible * 100) if total_possible > 0 else 0
                
                social_data['platforms'][platform] = platform_data
            
            # Calculate overall social coverage
            platform_scores = [data['coverage_score'] for data in social_data['platforms'].values()]
            social_data['overall_coverage'] = sum(platform_scores) / len(platform_scores) if platform_scores else 0
            social_data['social_score'] = social_data['overall_coverage']
            
            # Collect all missing tags
            for platform_data in social_data['platforms'].values():
                social_data['missing_tags'].extend(platform_data['missing_required'])
                social_data['missing_tags'].extend(platform_data['missing_recommended'])
            
        except Exception as e:
            logger.error(f"Error analyzing social meta tags: {str(e)}")
            
        return social_data
    
    def analyze_technical_tags(self, crawl_result, domain: str) -> Dict[str, Any]:
        """Analyze technical meta tags and HTML attributes"""
        tech_data = {
            'canonical_url': None,
            'robots_meta': None,
            'viewport_meta': None,
            'charset_meta': None,
            'lang_attribute': None,
            'hreflang_tags': [],
            'dns_prefetch': [],
            'preload_tags': [],
            'technical_score': 0
        }
        
        try:
            html_content = getattr(crawl_result, 'html', '')
            if not html_content:
                return tech_data
            
            # Canonical URL
            canonical_match = re.search(r'<link[^>]*rel=["\']canonical["\'][^>]*href=["\']([^"\']*)["\']', html_content, re.IGNORECASE)
            if canonical_match:
                tech_data['canonical_url'] = canonical_match.group(1)
            
            # Robots meta tag
            robots_match = re.search(r'<meta[^>]*name=["\']robots["\'][^>]*content=["\']([^"\']*)["\']', html_content, re.IGNORECASE)
            if robots_match:
                tech_data['robots_meta'] = robots_match.group(1)
            
            # Viewport meta tag
            viewport_match = re.search(r'<meta[^>]*name=["\']viewport["\'][^>]*content=["\']([^"\']*)["\']', html_content, re.IGNORECASE)
            if viewport_match:
                tech_data['viewport_meta'] = viewport_match.group(1)
            
            # Charset declaration
            charset_match = re.search(r'<meta[^>]*charset=["\']([^"\']*)["\']', html_content, re.IGNORECASE)
            if charset_match:
                tech_data['charset_meta'] = charset_match.group(1)
            
            # Language attribute
            lang_match = re.search(r'<html[^>]*lang=["\']([^"\']*)["\']', html_content, re.IGNORECASE)
            if lang_match:
                tech_data['lang_attribute'] = lang_match.group(1)
            
            # Hreflang tags
            hreflang_matches = re.findall(
                r'<link[^>]*rel=["\']alternate["\'][^>]*hreflang=["\']([^"\']*)["\'][^>]*href=["\']([^"\']*)["\']',
                html_content, re.IGNORECASE
            )
            tech_data['hreflang_tags'] = [{'lang': match[0], 'url': match[1]} for match in hreflang_matches]
            
            # DNS prefetch
            dns_prefetch_matches = re.findall(
                r'<link[^>]*rel=["\']dns-prefetch["\'][^>]*href=["\']([^"\']*)["\']',
                html_content, re.IGNORECASE
            )
            tech_data['dns_prefetch'] = dns_prefetch_matches
            
            # Preload tags
            preload_matches = re.findall(
                r'<link[^>]*rel=["\']preload["\'][^>]*href=["\']([^"\']*)["\'][^>]*as=["\']([^"\']*)["\']',
                html_content, re.IGNORECASE
            )
            tech_data['preload_tags'] = [{'href': match[0], 'as': match[1]} for match in preload_matches]
            
            # Calculate technical score
            tech_data['technical_score'] = self._calculate_technical_score(tech_data)
            
        except Exception as e:
            logger.error(f"Error analyzing technical tags: {str(e)}")
            
        return tech_data
    
    def analyze_robots_directives(self, crawl_result) -> Dict[str, Any]:
        """Analyze robots directives and crawling instructions"""
        robots_data = {
            'meta_robots': None,
            'meta_googlebot': None,
            'meta_bingbot': None,
            'directives': [],
            'crawling_allowed': True,
            'indexing_allowed': True,
            'following_allowed': True
        }
        
        try:
            html_content = getattr(crawl_result, 'html', '')
            if not html_content:
                return robots_data
            
            # Extract robots meta tags
            robots_patterns = [
                (r'<meta[^>]*name=["\']robots["\'][^>]*content=["\']([^"\']*)["\']', 'meta_robots'),
                (r'<meta[^>]*name=["\']googlebot["\'][^>]*content=["\']([^"\']*)["\']', 'meta_googlebot'),
                (r'<meta[^>]*name=["\']bingbot["\'][^>]*content=["\']([^"\']*)["\']', 'meta_bingbot')
            ]
            
            for pattern, key in robots_patterns:
                match = re.search(pattern, html_content, re.IGNORECASE)
                if match:
                    content = match.group(1).lower()
                    robots_data[key] = content
                    robots_data['directives'].extend(content.split(','))
            
            # Analyze directives
            all_directives = ' '.join(robots_data['directives']).lower()
            
            if 'noindex' in all_directives:
                robots_data['indexing_allowed'] = False
            if 'nofollow' in all_directives:
                robots_data['following_allowed'] = False
            if 'nocrawl' in all_directives or 'noarchive' in all_directives:
                robots_data['crawling_allowed'] = False
                
        except Exception as e:
            logger.error(f"Error analyzing robots directives: {str(e)}")
            
        return robots_data
    
    def analyze_mobile_optimization(self, crawl_result) -> Dict[str, Any]:
        """Analyze mobile optimization factors"""
        mobile_data = {
            'has_viewport': False,
            'viewport_content': None,
            'responsive_indicators': 0,
            'mobile_score': 0,
            'mobile_issues': []
        }
        
        try:
            html_content = getattr(crawl_result, 'html', '')
            if not html_content:
                return mobile_data
            
            # Viewport meta tag
            viewport_match = re.search(r'<meta[^>]*name=["\']viewport["\'][^>]*content=["\']([^"\']*)["\']', html_content, re.IGNORECASE)
            if viewport_match:
                mobile_data['has_viewport'] = True
                mobile_data['viewport_content'] = viewport_match.group(1)
                
                # Check for proper viewport configuration
                viewport_content = viewport_match.group(1).lower()
                if 'width=device-width' in viewport_content:
                    mobile_data['responsive_indicators'] += 1
                if 'initial-scale=1' in viewport_content:
                    mobile_data['responsive_indicators'] += 1
            else:
                mobile_data['mobile_issues'].append("Missing viewport meta tag")
            
            # Check for responsive design indicators
            responsive_patterns = [
                r'@media[^{]*\([^)]*max-width|min-width',  # CSS media queries
                r'class=["\'][^"\']*responsive[^"\']*["\']',  # Responsive CSS classes
                r'class=["\'][^"\']*mobile[^"\']*["\']',     # Mobile CSS classes
            ]
            
            for pattern in responsive_patterns:
                if re.search(pattern, html_content, re.IGNORECASE):
                    mobile_data['responsive_indicators'] += 1
            
            # Calculate mobile score
            max_indicators = 5  # viewport + scale + 3 responsive patterns
            mobile_data['mobile_score'] = (mobile_data['responsive_indicators'] / max_indicators * 100)
            
        except Exception as e:
            logger.error(f"Error analyzing mobile optimization: {str(e)}")
            
        return mobile_data
    
    def analyze_internationalization(self, crawl_result) -> Dict[str, Any]:
        """Analyze internationalization and localization"""
        i18n_data = {
            'lang_attribute': None,
            'hreflang_tags': [],
            'has_i18n': False,
            'i18n_score': 0
        }
        
        try:
            html_content = getattr(crawl_result, 'html', '')
            if not html_content:
                return i18n_data
            
            # Language attribute on html tag
            lang_match = re.search(r'<html[^>]*lang=["\']([^"\']*)["\']', html_content, re.IGNORECASE)
            if lang_match:
                i18n_data['lang_attribute'] = lang_match.group(1)
                i18n_data['has_i18n'] = True
            
            # Hreflang tags
            hreflang_matches = re.findall(
                r'<link[^>]*rel=["\']alternate["\'][^>]*hreflang=["\']([^"\']*)["\'][^>]*href=["\']([^"\']*)["\']',
                html_content, re.IGNORECASE
            )
            
            if hreflang_matches:
                i18n_data['hreflang_tags'] = [{'lang': match[0], 'url': match[1]} for match in hreflang_matches]
                i18n_data['has_i18n'] = True
            
            # Calculate i18n score
            score = 0
            if i18n_data['lang_attribute']:
                score += 50
            if i18n_data['hreflang_tags']:
                score += 50
            
            i18n_data['i18n_score'] = score
            
        except Exception as e:
            logger.error(f"Error analyzing internationalization: {str(e)}")
            
        return i18n_data
    
    def _extract_schema_types(self, schema_json) -> List[str]:
        """Extract schema types from JSON-LD"""
        types = []
        
        try:
            if isinstance(schema_json, dict):
                if '@type' in schema_json:
                    type_value = schema_json['@type']
                    if isinstance(type_value, list):
                        types.extend(type_value)
                    else:
                        types.append(type_value)
                
                # Recursively check nested objects
                for value in schema_json.values():
                    if isinstance(value, (dict, list)):
                        types.extend(self._extract_schema_types(value))
            
            elif isinstance(schema_json, list):
                for item in schema_json:
                    types.extend(self._extract_schema_types(item))
                    
        except Exception as e:
            logger.error(f"Error extracting schema types: {str(e)}")
            
        return types
    
    def _validate_schema_structure(self, schema_json) -> Dict[str, Any]:
        """Basic validation of schema structure"""
        validation = {'valid': True, 'errors': [], 'type': None}
        
        try:
            if isinstance(schema_json, dict) and '@type' in schema_json:
                schema_type = schema_json['@type']
                validation['type'] = schema_type
                
                # Basic required fields validation for common types
                required_fields = {
                    'Organization': ['name'],
                    'Person': ['name'],
                    'Product': ['name'],
                    'Article': ['headline', 'author'],
                    'LocalBusiness': ['name', 'address']
                }
                
                if schema_type in required_fields:
                    for field in required_fields[schema_type]:
                        if field not in schema_json:
                            validation['valid'] = False
                            validation['errors'].append(f"Missing required field '{field}' for {schema_type}")
            
        except Exception as e:
            validation['valid'] = False
            validation['errors'].append(f"Schema validation error: {str(e)}")
            
        return validation
    
    def _calculate_schema_coverage_score(self, schema_data: Dict[str, Any]) -> float:
        """Calculate schema markup coverage score"""
        score = 0
        
        # Points for having any schema
        if schema_data['has_schema']:
            score += 30
        
        # Points for JSON-LD (preferred format)
        if schema_data['json_ld_count'] > 0:
            score += 40
        
        # Points for important schema types
        important_types_found = sum(1 for t in schema_data['schema_types'] if t in self.important_schema_types)
        score += min(important_types_found * 10, 30)  # Max 30 points
        
        return min(score, 100)
    
    def _calculate_technical_score(self, tech_data: Dict[str, Any]) -> float:
        """Calculate technical SEO score"""
        score = 0
        max_score = 100
        
        # Canonical URL (20 points)
        if tech_data['canonical_url']:
            score += 20
        
        # Viewport meta (15 points)
        if tech_data['viewport_meta']:
            score += 15
        
        # Charset (10 points)
        if tech_data['charset_meta']:
            score += 10
        
        # Language attribute (15 points)
        if tech_data['lang_attribute']:
            score += 15
        
        # Robots meta (10 points)
        if tech_data['robots_meta']:
            score += 10
        
        # Hreflang (10 points)
        if tech_data['hreflang_tags']:
            score += 10
        
        # Performance hints (10 points)
        if tech_data['dns_prefetch'] or tech_data['preload_tags']:
            score += 10
        
        # Technical optimization bonus (10 points)
        if len(tech_data['preload_tags']) > 2:
            score += 10
        
        return min(score, max_score)
    
    def _identify_technical_issues(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify technical SEO issues"""
        issues = []
        
        # Schema issues
        schema_data = analysis.get('schema_markup', {})
        if not schema_data.get('has_schema'):
            issues.append({
                'type': 'missing_schema_markup',
                'severity': 'medium',
                'category': 'structured_data',
                'message': 'No structured data markup found',
                'recommendation': 'Add JSON-LD structured data for better search engine understanding',
                'impact': 'Reduced rich snippet opportunities'
            })
        
        if schema_data.get('schema_errors'):
            for error in schema_data['schema_errors']:
                issues.append({
                    'type': 'invalid_schema',
                    'severity': 'high',
                    'category': 'structured_data',
                    'message': f'Schema validation error: {error}',
                    'recommendation': 'Fix schema markup errors',
                    'impact': 'Invalid structured data may be ignored by search engines'
                })
        
        # Social meta tag issues
        social_data = analysis.get('social_meta_tags', {})
        if social_data.get('overall_coverage', 0) < 50:
            issues.append({
                'type': 'poor_social_meta',
                'severity': 'medium',
                'category': 'social_optimization',
                'message': 'Missing important social media meta tags',
                'recommendation': 'Add Open Graph and Twitter Card meta tags',
                'impact': 'Poor social media sharing experience'
            })
        
        # Technical tag issues
        tech_data = analysis.get('technical_tags', {})
        if not tech_data.get('canonical_url'):
            issues.append({
                'type': 'missing_canonical',
                'severity': 'high',
                'category': 'technical_seo',
                'message': 'Missing canonical URL',
                'recommendation': 'Add canonical link tag to prevent duplicate content issues',
                'impact': 'Potential duplicate content penalties'
            })
        
        if not tech_data.get('viewport_meta'):
            issues.append({
                'type': 'missing_viewport',
                'severity': 'high',
                'category': 'mobile_optimization',
                'message': 'Missing viewport meta tag',
                'recommendation': 'Add viewport meta tag for mobile optimization',
                'impact': 'Poor mobile user experience and SEO'
            })
        
        # Mobile optimization issues
        mobile_data = analysis.get('mobile_optimization', {})
        if mobile_data.get('mobile_score', 0) < 70:
            issues.append({
                'type': 'poor_mobile_optimization',
                'severity': 'high',
                'category': 'mobile_optimization',
                'message': 'Poor mobile optimization detected',
                'recommendation': 'Implement responsive design and mobile-first approach',
                'impact': 'Reduced mobile search rankings'
            })
        
        return issues
    
    def _generate_technical_opportunities(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate technical SEO improvement opportunities"""
        opportunities = []
        
        # Schema opportunities
        schema_data = analysis.get('schema_markup', {})
        if schema_data.get('coverage_score', 0) < 80:
            opportunities.append({
                'category': 'Structured Data',
                'title': 'Enhance structured data markup',
                'description': 'Add comprehensive schema markup for better search engine understanding',
                'impact': 'High',
                'effort': 'Medium',
                'implementation': 'Add JSON-LD for Organization, Product, Article, or other relevant schema types'
            })
        
        # Social media opportunities
        social_data = analysis.get('social_meta_tags', {})
        if social_data.get('overall_coverage', 0) < 90:
            opportunities.append({
                'category': 'Social Optimization',
                'title': 'Complete social media meta tags',
                'description': 'Add missing Open Graph and Twitter Card tags',
                'impact': 'Medium',
                'effort': 'Low',
                'implementation': 'Add og:image, twitter:card, and other missing social meta tags'
            })
        
        # Technical performance opportunities
        tech_data = analysis.get('technical_tags', {})
        if not tech_data.get('preload_tags'):
            opportunities.append({
                'category': 'Performance',
                'title': 'Implement resource preloading',
                'description': 'Preload critical resources for faster page loading',
                'impact': 'Medium',
                'effort': 'Low',
                'implementation': 'Add <link rel="preload"> for critical CSS, fonts, and images'
            })
        
        # International SEO opportunities
        i18n_data = analysis.get('internationalization', {})
        if not i18n_data.get('has_i18n') and i18n_data.get('i18n_score', 0) < 50:
            opportunities.append({
                'category': 'International SEO',
                'title': 'Implement internationalization',
                'description': 'Add language declarations and hreflang tags for better international SEO',
                'impact': 'Medium',
                'effort': 'Medium',
                'implementation': 'Add lang attribute to HTML tag and hreflang tags for multiple language versions'
            })
        
        return opportunities