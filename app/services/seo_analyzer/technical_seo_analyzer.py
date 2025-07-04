"""
Refactored Technical SEO Analyzer - Modular Architecture
Main coordinator that uses specialized analyzers for different aspects
"""
from typing import Dict, List, Any, Optional
import logging
import re
from urllib.parse import urlparse

from .technical.schema_analyzer import SchemaAnalyzer
from .technical.social_meta_analyzer import SocialMetaAnalyzer
from .technical.technical_tags_analyzer import TechnicalTagsAnalyzer
from app.services.url_utils import clean_url, normalize_url

logger = logging.getLogger(__name__)

class TechnicalSEOAnalyzer:
    """Refactored Technical SEO analyzer using modular components"""
    
    def __init__(self):
        # Initialize specialized analyzers
        self.schema_analyzer = SchemaAnalyzer()
        self.social_analyzer = SocialMetaAnalyzer()
        self.technical_tags_analyzer = TechnicalTagsAnalyzer()
    
    def analyze_technical_seo(self, crawl_result, domain: str) -> Dict[str, Any]:
        """Comprehensive technical SEO analysis using modular components"""
        analysis = {
            'schema_markup': self.schema_analyzer.analyze_schema_markup(crawl_result),
            'social_meta_tags': self.social_analyzer.analyze_social_meta_tags(crawl_result),
            'technical_tags': self.technical_tags_analyzer.analyze_technical_tags(crawl_result, domain),
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
    
    def analyze_robots_directives(self, crawl_result) -> Dict[str, Any]:
        """Analyze robots.txt and robots meta directives"""
        robots_data = {
            'meta_robots': {
                'present': False,
                'directives': [],
                'issues': []
            },
            'robots_txt': {
                'accessible': False,
                'content': None,
                'disallowed_paths': [],
                'crawl_delay': None,
                'sitemap_references': []
            },
            'recommendations': []
        }
        
        try:
            html_content = getattr(crawl_result, 'html', '')
            
            # Analyze meta robots (delegated to technical_tags_analyzer)
            tech_analysis = self.technical_tags_analyzer.analyze_technical_tags(crawl_result, '')
            robots_data['meta_robots'] = tech_analysis['robots_meta']
            
            # robots.txt analysis would need additional HTTP request
            # This is a simplified version focusing on meta robots
            
        except Exception as e:
            logger.error(f"Error analyzing robots directives: {str(e)}")
            robots_data['error'] = str(e)
        
        return robots_data
    
    def analyze_mobile_optimization(self, crawl_result) -> Dict[str, Any]:
        """Analyze mobile optimization factors"""
        mobile_data = {
            'viewport_tag': {
                'present': False,
                'content': None,
                'is_responsive': False
            },
            'mobile_friendly_score': 0,
            'touch_elements': {
                'count': 0,
                'properly_sized': True
            },
            'font_size': {
                'is_readable': True,
                'issues': []
            },
            'content_sizing': {
                'fits_viewport': True,
                'horizontal_scroll': False
            },
            'recommendations': []
        }
        
        try:
            html_content = getattr(crawl_result, 'html', '')
            
            # Get viewport analysis from technical_tags_analyzer
            tech_analysis = self.technical_tags_analyzer.analyze_technical_tags(crawl_result, '')
            mobile_data['viewport_tag'] = tech_analysis['viewport']
            
            # Basic mobile optimization checks
            if mobile_data['viewport_tag']['is_mobile_friendly']:
                mobile_data['mobile_friendly_score'] += 40
            
            # Check for responsive design indicators
            if self._has_responsive_design_indicators(html_content):
                mobile_data['mobile_friendly_score'] += 30
                mobile_data['content_sizing']['fits_viewport'] = True
            
            # Check for mobile-specific meta tags
            if self._has_mobile_meta_tags(html_content):
                mobile_data['mobile_friendly_score'] += 15
            
            # Check for touch-friendly elements
            touch_score = self._analyze_touch_elements(html_content)
            mobile_data['touch_elements'] = touch_score
            mobile_data['mobile_friendly_score'] += touch_score['score']
            
            # Generate recommendations
            mobile_data['recommendations'] = self._generate_mobile_recommendations(mobile_data)
            
        except Exception as e:
            logger.error(f"Error analyzing mobile optimization: {str(e)}")
            mobile_data['error'] = str(e)
        
        return mobile_data
    
    def analyze_internationalization(self, crawl_result) -> Dict[str, Any]:
        """Analyze internationalization and localization factors"""
        i18n_data = {
            'lang_attribute': {
                'present': False,
                'value': None,
                'is_valid': True
            },
            'hreflang_tags': {
                'present': False,
                'count': 0,
                'languages': [],
                'issues': []
            },
            'content_language': {
                'detected': None,
                'confidence': 0
            },
            'currency_symbols': [],
            'date_formats': [],
            'recommendations': []
        }
        
        try:
            # Get lang and hreflang analysis from technical_tags_analyzer
            tech_analysis = self.technical_tags_analyzer.analyze_technical_tags(crawl_result, '')
            i18n_data['lang_attribute'] = tech_analysis['lang_attr']
            i18n_data['hreflang_tags'] = tech_analysis['hreflang']
            
            # Simple content language detection
            html_content = getattr(crawl_result, 'html', '')
            i18n_data['content_language'] = self._detect_content_language(html_content)
            
            # Generate recommendations
            i18n_data['recommendations'] = self._generate_i18n_recommendations(i18n_data)
            
        except Exception as e:
            logger.error(f"Error analyzing internationalization: {str(e)}")
            i18n_data['error'] = str(e)
        
        return i18n_data
    
    def _has_responsive_design_indicators(self, html_content: str) -> bool:
        """Check for responsive design indicators"""
        indicators = [
            r'@media\s*\([^)]*\)',  # CSS media queries
            r'viewport\s*=.*device-width',  # Viewport meta tag
            r'responsive',  # Responsive keywords in CSS classes
            r'col-\w+',  # Bootstrap grid classes
            r'flex\w*',  # Flexbox classes
            r'grid\w*'  # CSS Grid classes
        ]
        
        return any(re.search(pattern, html_content, re.IGNORECASE) for pattern in indicators)
    
    def _has_mobile_meta_tags(self, html_content: str) -> bool:
        """Check for mobile-specific meta tags"""
        mobile_tags = [
            r'name=["\']format-detection["\']',
            r'name=["\']mobile-web-app-capable["\']',
            r'name=["\']apple-mobile-web-app-capable["\']'
        ]
        
        return any(re.search(tag, html_content, re.IGNORECASE) for tag in mobile_tags)
    
    def _analyze_touch_elements(self, html_content: str) -> Dict[str, Any]:
        """Analyze touch-friendly elements"""
        touch_data = {
            'count': 0,
            'properly_sized': True,
            'score': 0
        }
        
        # Count interactive elements
        interactive_patterns = [
            r'<button[^>]*>',
            r'<a[^>]*href[^>]*>',
            r'<input[^>]*type=["\'](?:button|submit|reset)["\'][^>]*>',
            r'onclick=["\'][^"\']*["\']'
        ]
        
        for pattern in interactive_patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            touch_data['count'] += len(matches)
        
        # Basic scoring
        if touch_data['count'] > 0:
            touch_data['score'] = 15
        
        return touch_data
    
    def _detect_content_language(self, html_content: str) -> Dict[str, Any]:
        """Simple content language detection"""
        # This is a very basic implementation
        # In a production system, you'd use a proper language detection library
        
        language_indicators = {
            'italian': ['e ', 'di ', 'la ', 'il ', 'che ', 'è ', 'per ', 'con ', 'dei ', 'delle '],
            'english': ['the ', 'and ', 'of ', 'to ', 'a ', 'in ', 'is ', 'it ', 'you ', 'that '],
            'spanish': ['el ', 'de ', 'que ', 'y ', 'en ', 'un ', 'es ', 'se ', 'no ', 'te '],
            'french': ['le ', 'de ', 'et ', 'à ', 'un ', 'il ', 'être ', 'et ', 'en ', 'avoir '],
            'german': ['der ', 'die ', 'und ', 'in ', 'den ', 'von ', 'zu ', 'das ', 'mit ', 'sich ']
        }
        
        # Extract text content (very basic)
        text_content = re.sub(r'<[^>]+>', ' ', html_content).lower()
        
        best_language = None
        best_score = 0
        
        for language, indicators in language_indicators.items():
            score = sum(text_content.count(indicator) for indicator in indicators)
            if score > best_score:
                best_score = score
                best_language = language
        
        confidence = min(best_score / 100, 1.0) if best_score > 0 else 0
        
        return {
            'detected': best_language,
            'confidence': confidence
        }
    
    def _generate_mobile_recommendations(self, mobile_data: Dict[str, Any]) -> List[str]:
        """Generate mobile optimization recommendations"""
        recommendations = []
        
        if not mobile_data['viewport_tag']['present']:
            recommendations.append("Add viewport meta tag for mobile optimization")
        elif not mobile_data['viewport_tag']['is_mobile_friendly']:
            recommendations.append("Update viewport meta tag to include 'width=device-width'")
        
        if mobile_data['mobile_friendly_score'] < 70:
            recommendations.append("Improve mobile responsiveness with CSS media queries")
        
        if not mobile_data['content_sizing']['fits_viewport']:
            recommendations.append("Ensure content fits within viewport width")
        
        return recommendations
    
    def _generate_i18n_recommendations(self, i18n_data: Dict[str, Any]) -> List[str]:
        """Generate internationalization recommendations"""
        recommendations = []
        
        if not i18n_data['lang_attribute']['present']:
            recommendations.append("Add lang attribute to HTML element for better accessibility")
        
        if i18n_data['hreflang_tags']['present'] and i18n_data['hreflang_tags']['issues']:
            recommendations.append("Fix hreflang implementation issues")
        
        return recommendations
    
    def _calculate_technical_score(self, tech_data: Dict[str, Any]) -> float:
        """Calculate overall technical SEO score"""
        scores = []
        
        # Schema markup score (25% weight)
        schema_score = tech_data['schema_markup'].get('coverage_score', 0)
        scores.append(schema_score * 0.25)
        
        # Social meta score (20% weight)
        social_score = tech_data['social_meta_tags'].get('overall_score', 0)
        scores.append(social_score * 0.20)
        
        # Technical tags score (25% weight)
        technical_score = tech_data['technical_tags'].get('technical_score', 0)
        scores.append(technical_score * 0.25)
        
        # Mobile optimization score (20% weight)
        mobile_score = tech_data['mobile_optimization'].get('mobile_friendly_score', 0)
        scores.append(mobile_score * 0.20)
        
        # Internationalization score (10% weight)
        i18n_score = self._calculate_i18n_score(tech_data['internationalization'])
        scores.append(i18n_score * 0.10)
        
        return sum(scores)
    
    def _calculate_i18n_score(self, i18n_data: Dict[str, Any]) -> float:
        """Calculate internationalization score"""
        score = 0.0
        
        if i18n_data['lang_attribute']['present']:
            score += 50.0
            if i18n_data['lang_attribute']['is_valid']:
                score += 25.0
        
        if i18n_data['hreflang_tags']['present']:
            score += 25.0
        
        return score
    
    def _identify_technical_issues(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify technical SEO issues"""
        issues = []
        
        # Schema issues
        schema_data = analysis['schema_markup']
        if not schema_data['has_schema']:
            issues.append({
                'type': 'missing_schema',
                'severity': 'medium',
                'category': 'technical',
                'title': 'Missing Schema Markup',
                'description': 'Page lacks structured data markup',
                'recommendation': 'Add relevant Schema.org markup'
            })
        
        # Social meta issues
        social_data = analysis['social_meta_tags']
        if not social_data['open_graph']['present']:
            issues.append({
                'type': 'missing_og_tags',
                'severity': 'medium',
                'category': 'technical',
                'title': 'Missing Open Graph Tags',
                'description': 'Page lacks Open Graph meta tags for social sharing',
                'recommendation': 'Add Open Graph meta tags'
            })
        
        # Technical tag issues
        tech_data = analysis['technical_tags']
        if not tech_data['canonical']['present']:
            issues.append({
                'type': 'missing_canonical',
                'severity': 'high',
                'category': 'technical',
                'title': 'Missing Canonical URL',
                'description': 'Page lacks canonical URL specification',
                'recommendation': 'Add canonical link tag'
            })
        
        if not tech_data['viewport']['present']:
            issues.append({
                'type': 'missing_viewport',
                'severity': 'high',
                'category': 'technical',
                'title': 'Missing Viewport Meta Tag',
                'description': 'Page lacks viewport meta tag for mobile optimization',
                'recommendation': 'Add viewport meta tag with device-width'
            })
        
        return issues
    
    def _generate_technical_opportunities(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate technical SEO opportunities"""
        opportunities = []
        
        schema_data = analysis['schema_markup']
        if schema_data['has_schema'] and schema_data['coverage_score'] < 80:
            opportunities.append({
                'category': 'Schema Enhancement',
                'title': 'Expand structured data coverage',
                'description': f"Current schema coverage: {schema_data['coverage_score']:.0f}%",
                'impact': 'Medium',
                'effort': 'Low',
                'implementation': 'Add missing schema types based on page content'
            })
        
        social_data = analysis['social_meta_tags']
        if social_data['overall_score'] < 80:
            opportunities.append({
                'category': 'Social Optimization',
                'title': 'Improve social media optimization',
                'description': f"Current social score: {social_data['overall_score']:.0f}%",
                'impact': 'Medium',
                'effort': 'Low',
                'implementation': 'Complete Open Graph and Twitter Card implementations'
            })
        
        return opportunities
    
    # Delegation methods for backward compatibility
    def analyze_schema_markup(self, crawl_result) -> Dict[str, Any]:
        """Delegate to schema analyzer"""
        return self.schema_analyzer.analyze_schema_markup(crawl_result)
    
    def analyze_social_meta_tags(self, crawl_result) -> Dict[str, Any]:
        """Delegate to social meta analyzer"""
        return self.social_analyzer.analyze_social_meta_tags(crawl_result)
    
    def analyze_technical_tags(self, crawl_result, domain: str) -> Dict[str, Any]:
        """Delegate to technical tags analyzer"""
        return self.technical_tags_analyzer.analyze_technical_tags(crawl_result, domain)
    
    def extract_canonical_url(self, crawl_result) -> Optional[str]:
        """Delegate to technical tags analyzer"""
        return self.technical_tags_analyzer.extract_canonical_url(crawl_result)
    
    def analyze_url_structure(self, url: str) -> Dict[str, Any]:
        """Analyze URL structure for SEO"""
        analysis = {
            'url': url,
            'is_seo_friendly': True,
            'issues': [],
            'recommendations': [],
            'score': 100
        }
        
        try:
            parsed = urlparse(url)
            
            # URL length check
            if len(url) > 100:
                analysis['issues'].append('URL is longer than 100 characters')
                analysis['score'] -= 10
                analysis['is_seo_friendly'] = False
            
            # Check for parameters
            if parsed.query:
                analysis['issues'].append('URL contains query parameters')
                analysis['score'] -= 5
            
            # Check for underscores
            if '_' in parsed.path:
                analysis['issues'].append('URL contains underscores (use hyphens instead)')
                analysis['score'] -= 5
                analysis['is_seo_friendly'] = False
            
            # Check for uppercase letters
            if any(c.isupper() for c in parsed.path):
                analysis['issues'].append('URL contains uppercase letters')
                analysis['score'] -= 5
                analysis['is_seo_friendly'] = False
            
            # Check for stop words
            stop_words = ['a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by']
            path_words = parsed.path.lower().split('/')
            for word in stop_words:
                if word in path_words:
                    analysis['recommendations'].append(f'Consider removing stop word: {word}')
            
            # Check for dynamic parameters
            dynamic_indicators = ['id=', 'page=', 'category=', 'product=']
            if any(indicator in url.lower() for indicator in dynamic_indicators):
                analysis['recommendations'].append('Consider using URL rewriting for cleaner URLs')
            
        except Exception as e:
            logger.error(f"Error analyzing URL structure: {str(e)}")
            analysis['error'] = str(e)
        
        return analysis
    
    def detect_duplicate_content_issues(self, pages_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect potential duplicate content issues"""
        duplicate_analysis = {
            'potential_duplicates': [],
            'canonical_issues': [],
            'recommendations': []
        }
        
        try:
            # Group pages by similar content indicators
            title_groups = {}
            description_groups = {}
            
            for page in pages_data:
                title = page.get('title', '').strip().lower()
                description = page.get('meta_description', '').strip().lower()
                
                if title:
                    if title not in title_groups:
                        title_groups[title] = []
                    title_groups[title].append(page)
                
                if description:
                    if description not in description_groups:
                        description_groups[description] = []
                    description_groups[description].append(page)
            
            # Find duplicates
            for title, pages in title_groups.items():
                if len(pages) > 1:
                    duplicate_analysis['potential_duplicates'].append({
                        'type': 'duplicate_title',
                        'title': title,
                        'pages': [p.get('url') for p in pages],
                        'count': len(pages)
                    })
            
            for description, pages in description_groups.items():
                if len(pages) > 1:
                    duplicate_analysis['potential_duplicates'].append({
                        'type': 'duplicate_description',
                        'description': description[:100] + '...',
                        'pages': [p.get('url') for p in pages],
                        'count': len(pages)
                    })
            
            # Generate recommendations
            if duplicate_analysis['potential_duplicates']:
                duplicate_analysis['recommendations'].append(
                    'Review and consolidate duplicate content or implement proper canonicalization'
                )
                duplicate_analysis['recommendations'].append(
                    'Ensure each page has unique title tags and meta descriptions'
                )
        
        except Exception as e:
            logger.error(f"Error detecting duplicate content: {str(e)}")
            duplicate_analysis['error'] = str(e)
        
        return duplicate_analysis