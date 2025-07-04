"""
Social Media Meta Tags Analyzer
Analyzes Open Graph, Twitter Cards, and other social media meta tags
"""
from typing import Dict, List, Any, Optional
import logging
import re
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class SocialMetaAnalyzer:
    """Analyzes social media meta tags"""
    
    def __init__(self):
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
    
    def analyze_social_meta_tags(self, crawl_result) -> Dict[str, Any]:
        """Analyze social media meta tags"""
        social_data = {
            'open_graph': {
                'present': False,
                'tags': {},
                'completeness_score': 0,
                'missing_tags': [],
                'issues': []
            },
            'twitter_cards': {
                'present': False,
                'tags': {},
                'completeness_score': 0,
                'missing_tags': [],
                'issues': []
            },
            'other_social': {
                'tags': {},
                'platforms': []
            },
            'overall_score': 0,
            'recommendations': []
        }
        
        try:
            html_content = getattr(crawl_result, 'html', '')
            if not html_content:
                return social_data
            
            # Extract all meta tags
            meta_tags = self._extract_meta_tags(html_content)
            
            # Analyze Open Graph tags
            social_data['open_graph'] = self._analyze_open_graph(meta_tags)
            
            # Analyze Twitter Card tags
            social_data['twitter_cards'] = self._analyze_twitter_cards(meta_tags)
            
            # Analyze other social platforms
            social_data['other_social'] = self._analyze_other_social_tags(meta_tags)
            
            # Calculate overall score
            social_data['overall_score'] = self._calculate_social_score(social_data)
            
            # Generate recommendations
            social_data['recommendations'] = self._generate_social_recommendations(social_data)
            
        except Exception as e:
            logger.error(f"Error analyzing social meta tags: {str(e)}")
            social_data['error'] = str(e)
        
        return social_data
    
    def _extract_meta_tags(self, html_content: str) -> Dict[str, str]:
        """Extract all meta tags from HTML"""
        meta_tags = {}
        
        # Pattern to match meta tags with property attribute (Open Graph, etc.)
        property_pattern = r'<meta[^>]*property=["\']([^"\']+)["\'][^>]*content=["\']([^"\']*)["\'][^>]*/?>'
        property_matches = re.findall(property_pattern, html_content, re.IGNORECASE)
        
        for prop, content in property_matches:
            meta_tags[prop.lower()] = content
        
        # Pattern to match meta tags with name attribute (Twitter Cards, etc.)
        name_pattern = r'<meta[^>]*name=["\']([^"\']+)["\'][^>]*content=["\']([^"\']*)["\'][^>]*/?>'
        name_matches = re.findall(name_pattern, html_content, re.IGNORECASE)
        
        for name, content in name_matches:
            meta_tags[name.lower()] = content
        
        return meta_tags
    
    def _analyze_open_graph(self, meta_tags: Dict[str, str]) -> Dict[str, Any]:
        """Analyze Open Graph meta tags"""
        og_data = {
            'present': False,
            'tags': {},
            'completeness_score': 0,
            'missing_tags': [],
            'issues': []
        }
        
        # Extract Open Graph tags
        og_tags = {k: v for k, v in meta_tags.items() if k.startswith('og:')}
        
        if og_tags:
            og_data['present'] = True
            og_data['tags'] = og_tags
            
            # Check required tags
            required_tags = self.social_platforms['facebook']['required']
            missing_required = [tag for tag in required_tags if tag not in og_tags]
            og_data['missing_tags'] = missing_required
            
            # Validate content
            self._validate_og_content(og_tags, og_data['issues'])
            
            # Calculate completeness score
            total_possible = len(required_tags) + len(self.social_platforms['facebook']['recommended'])
            present_tags = len([tag for tag in required_tags + self.social_platforms['facebook']['recommended'] if tag in og_tags])
            og_data['completeness_score'] = (present_tags / total_possible) * 100
        
        return og_data
    
    def _analyze_twitter_cards(self, meta_tags: Dict[str, str]) -> Dict[str, Any]:
        """Analyze Twitter Card meta tags"""
        twitter_data = {
            'present': False,
            'tags': {},
            'completeness_score': 0,
            'missing_tags': [],
            'issues': []
        }
        
        # Extract Twitter Card tags
        twitter_tags = {k: v for k, v in meta_tags.items() if k.startswith('twitter:')}
        
        if twitter_tags:
            twitter_data['present'] = True
            twitter_data['tags'] = twitter_tags
            
            # Check required tags
            required_tags = self.social_platforms['twitter']['required']
            missing_required = [tag for tag in required_tags if tag not in twitter_tags]
            twitter_data['missing_tags'] = missing_required
            
            # Validate content
            self._validate_twitter_content(twitter_tags, twitter_data['issues'])
            
            # Calculate completeness score
            total_possible = len(required_tags) + len(self.social_platforms['twitter']['recommended'])
            present_tags = len([tag for tag in required_tags + self.social_platforms['twitter']['recommended'] if tag in twitter_tags])
            twitter_data['completeness_score'] = (present_tags / total_possible) * 100
        
        return twitter_data
    
    def _analyze_other_social_tags(self, meta_tags: Dict[str, str]) -> Dict[str, Any]:
        """Analyze other social platform tags"""
        other_data = {
            'tags': {},
            'platforms': []
        }
        
        # Look for Facebook-specific tags
        fb_tags = {k: v for k, v in meta_tags.items() if k.startswith('fb:')}
        if fb_tags:
            other_data['tags'].update(fb_tags)
            other_data['platforms'].append('facebook_extended')
        
        # Look for other social platform indicators
        social_indicators = {
            'pinterest': ['pinterest-rich-pin'],
            'linkedin': ['linkedin:owner'],
            'whatsapp': ['whatsapp:']
        }
        
        for platform, indicators in social_indicators.items():
            for indicator in indicators:
                if any(indicator in tag for tag in meta_tags.keys()):
                    other_data['platforms'].append(platform)
                    break
        
        return other_data
    
    def _validate_og_content(self, og_tags: Dict[str, str], issues: List[str]):
        """Validate Open Graph content"""
        
        # Check og:image
        if 'og:image' in og_tags:
            image_url = og_tags['og:image']
            if not image_url.startswith(('http://', 'https://')):
                issues.append("og:image should be an absolute URL")
            elif not any(ext in image_url.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                issues.append("og:image should point to a valid image file")
        
        # Check og:url
        if 'og:url' in og_tags:
            url = og_tags['og:url']
            if not url.startswith(('http://', 'https://')):
                issues.append("og:url should be an absolute URL")
        
        # Check og:title length
        if 'og:title' in og_tags:
            title = og_tags['og:title']
            if len(title) > 95:
                issues.append("og:title is too long (recommended max 95 characters)")
        
        # Check og:description length
        if 'og:description' in og_tags:
            description = og_tags['og:description']
            if len(description) > 300:
                issues.append("og:description is too long (recommended max 300 characters)")
            elif len(description) < 150:
                issues.append("og:description is too short (recommended min 150 characters)")
    
    def _validate_twitter_content(self, twitter_tags: Dict[str, str], issues: List[str]):
        """Validate Twitter Card content"""
        
        # Check twitter:card value
        if 'twitter:card' in twitter_tags:
            card_type = twitter_tags['twitter:card']
            valid_types = ['summary', 'summary_large_image', 'app', 'player']
            if card_type not in valid_types:
                issues.append(f"Invalid twitter:card type '{card_type}'. Valid types: {', '.join(valid_types)}")
        
        # Check twitter:image
        if 'twitter:image' in twitter_tags:
            image_url = twitter_tags['twitter:image']
            if not image_url.startswith(('http://', 'https://')):
                issues.append("twitter:image should be an absolute URL")
        
        # Check twitter:title length
        if 'twitter:title' in twitter_tags:
            title = twitter_tags['twitter:title']
            if len(title) > 70:
                issues.append("twitter:title is too long (recommended max 70 characters)")
        
        # Check twitter:description length
        if 'twitter:description' in twitter_tags:
            description = twitter_tags['twitter:description']
            if len(description) > 200:
                issues.append("twitter:description is too long (recommended max 200 characters)")
    
    def _calculate_social_score(self, social_data: Dict[str, Any]) -> float:
        """Calculate overall social media optimization score"""
        score = 0.0
        
        # Open Graph score (60% weight)
        og_score = social_data['open_graph']['completeness_score']
        score += og_score * 0.6
        
        # Twitter Cards score (30% weight)
        twitter_score = social_data['twitter_cards']['completeness_score']
        score += twitter_score * 0.3
        
        # Other platforms score (10% weight)
        other_platforms = len(social_data['other_social']['platforms'])
        other_score = min(other_platforms * 25, 100)  # 25 points per platform, max 100
        score += other_score * 0.1
        
        # Penalty for issues
        total_issues = len(social_data['open_graph']['issues']) + len(social_data['twitter_cards']['issues'])
        penalty = min(total_issues * 5, 20)  # 5 points per issue, max 20 penalty
        
        return max(0.0, min(100.0, score - penalty))
    
    def _generate_social_recommendations(self, social_data: Dict[str, Any]) -> List[str]:
        """Generate social media optimization recommendations"""
        recommendations = []
        
        # Open Graph recommendations
        if not social_data['open_graph']['present']:
            recommendations.append("Add Open Graph meta tags for better Facebook/LinkedIn sharing")
        elif social_data['open_graph']['missing_tags']:
            missing = ', '.join(social_data['open_graph']['missing_tags'])
            recommendations.append(f"Add missing Open Graph tags: {missing}")
        
        # Twitter Cards recommendations
        if not social_data['twitter_cards']['present']:
            recommendations.append("Add Twitter Card meta tags for better Twitter sharing")
        elif social_data['twitter_cards']['missing_tags']:
            missing = ', '.join(social_data['twitter_cards']['missing_tags'])
            recommendations.append(f"Add missing Twitter Card tags: {missing}")
        
        # Issue-based recommendations
        if social_data['open_graph']['issues']:
            recommendations.append("Fix Open Graph validation issues for better social sharing")
        
        if social_data['twitter_cards']['issues']:
            recommendations.append("Fix Twitter Card validation issues for better Twitter sharing")
        
        # General recommendations
        if social_data['overall_score'] < 70:
            recommendations.append("Improve social media meta tags to enhance sharing appearance")
        
        return recommendations[:5]  # Limit to top 5 recommendations