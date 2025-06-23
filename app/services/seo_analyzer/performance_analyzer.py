"""
Core Web Vitals Performance Analyzer
Analyzes page performance metrics crucial for Google's ranking algorithm
"""
from typing import Dict, List, Any, Optional
import logging
import re
from urllib.parse import urlparse
from .core.resource_details import ResourceDetailsBuilder, IssueFactory
from app.services.url_utils import clean_url

logger = logging.getLogger(__name__)

class PerformanceAnalyzer:
    """Analyzes Core Web Vitals and performance metrics"""
    
    def __init__(self):
        # Core Web Vitals thresholds (2024/2025 standards)
        self.cwv_thresholds = {
            'lcp': {'good': 2.5, 'needs_improvement': 4.0},  # Largest Contentful Paint (seconds)
            'fid': {'good': 100, 'needs_improvement': 300},   # First Input Delay (ms)
            'cls': {'good': 0.1, 'needs_improvement': 0.25}, # Cumulative Layout Shift
            'fcp': {'good': 1.8, 'needs_improvement': 3.0},  # First Contentful Paint (seconds)
            'ttfb': {'good': 600, 'needs_improvement': 1500}, # Time to First Byte (ms)
            'speed_index': {'good': 3.4, 'needs_improvement': 5.8}  # Speed Index (seconds)
        }
        
        # Performance impact indicators
        self.performance_indicators = {
            'heavy_images': {'threshold': 500000, 'impact': 'high'},     # 500KB+ images
            'many_requests': {'threshold': 100, 'impact': 'medium'},     # 100+ requests
            'large_css': {'threshold': 100000, 'impact': 'medium'},      # 100KB+ CSS
            'large_js': {'threshold': 200000, 'impact': 'high'},         # 200KB+ JavaScript
            'no_compression': {'impact': 'high'},
            'blocking_resources': {'impact': 'high'}
        }
    
    def analyze_core_web_vitals(self, crawl_result) -> Dict[str, Any]:
        """Extract and analyze Core Web Vitals from crawl result"""
        performance_data = {
            'metrics': {},
            'scores': {},
            'performance_issues': [],
            'optimization_opportunities': []
        }
        
        try:
            # Extract timing data from crawl result
            metrics = self._extract_performance_metrics(crawl_result)
            performance_data['metrics'] = metrics
            
            # Calculate scores for each metric
            scores = self._calculate_cwv_scores(metrics)
            performance_data['scores'] = scores
            
            # Identify performance issues
            issues = self._identify_performance_issues(crawl_result, metrics)
            performance_data['performance_issues'] = issues
            
            # Generate optimization opportunities
            opportunities = self._generate_optimization_opportunities(metrics, crawl_result)
            performance_data['optimization_opportunities'] = opportunities
            
            logger.info(f"Core Web Vitals analysis completed for {crawl_result.url}")
            
        except Exception as e:
            logger.error(f"Error analyzing Core Web Vitals for {crawl_result.url}: {str(e)}")
            
        return performance_data
    
    def _extract_performance_metrics(self, crawl_result) -> Dict[str, float]:
        """Extract performance timing metrics from crawl result"""
        metrics = {}
        
        try:
            # Get response time as base metric
            response_time = getattr(crawl_result, 'response_time', None)
            if response_time:
                metrics['response_time'] = response_time
                # Estimate TTFB from response time
                metrics['ttfb'] = response_time * 1000  # Convert to ms
            
            # Extract content size
            content_length = len(getattr(crawl_result, 'html', ''))
            metrics['content_size'] = content_length
            
            # Analyze HTML structure for performance indicators
            html_content = getattr(crawl_result, 'html', '')
            if html_content:
                # Count resource requests
                metrics['image_count'] = len(re.findall(r'<img[^>]*>', html_content, re.IGNORECASE))
                metrics['css_count'] = len(re.findall(r'<link[^>]*rel=["\']stylesheet["\'][^>]*>', html_content, re.IGNORECASE))
                metrics['js_count'] = len(re.findall(r'<script[^>]*src=[^>]*>', html_content, re.IGNORECASE))
                
                # Estimate blocking resources
                blocking_css = len(re.findall(r'<link[^>]*rel=["\']stylesheet["\'][^>]*(?!media=["\']print["\'])', html_content, re.IGNORECASE))
                blocking_js = len(re.findall(r'<script[^>]*src=[^>]*(?!async|defer)', html_content, re.IGNORECASE))
                metrics['blocking_resources'] = blocking_css + blocking_js
                
                # Estimate FCP based on content structure
                has_above_fold_content = bool(re.search(r'<h1[^>]*>|<p[^>]*>|<div[^>]*>', html_content[:2000], re.IGNORECASE))
                if has_above_fold_content and response_time:
                    metrics['fcp_estimate'] = response_time + 0.3  # Add rendering time estimate
                
                # Estimate LCP based on largest content
                largest_image = re.search(r'<img[^>]*(?:width=["\'](\d+)["\']|height=["\'](\d+)["\'])', html_content, re.IGNORECASE)
                if largest_image and response_time:
                    metrics['lcp_estimate'] = response_time + 0.5  # Add image loading time
                
                # Simple CLS estimation (high if many images without dimensions)
                images_without_dims = len(re.findall(r'<img(?![^>]*(?:width|height))[^>]*>', html_content, re.IGNORECASE))
                metrics['cls_risk'] = min(images_without_dims * 0.05, 0.5)  # Scale to CLS range
            
        except Exception as e:
            logger.error(f"Error extracting performance metrics: {str(e)}")
            
        return metrics
    
    def _calculate_cwv_scores(self, metrics: Dict[str, float]) -> Dict[str, Dict[str, Any]]:
        """Calculate performance scores for Core Web Vitals"""
        scores = {}
        
        for metric_name, thresholds in self.cwv_thresholds.items():
            if f"{metric_name}_estimate" in metrics:
                value = metrics[f"{metric_name}_estimate"]
            elif metric_name in metrics:
                value = metrics[metric_name]
            elif metric_name == 'cls' and 'cls_risk' in metrics:
                value = metrics['cls_risk']
            elif metric_name == 'ttfb' and 'ttfb' in metrics:
                value = metrics['ttfb']
            else:
                continue
                
            # Calculate score (0-100)
            if value <= thresholds['good']:
                score = 90 + (thresholds['good'] - value) / thresholds['good'] * 10
                rating = 'good'
            elif value <= thresholds['needs_improvement']:
                score = 50 + (thresholds['needs_improvement'] - value) / (thresholds['needs_improvement'] - thresholds['good']) * 40
                rating = 'needs_improvement'
            else:
                score = max(0, 50 - (value - thresholds['needs_improvement']) / thresholds['needs_improvement'] * 50)
                rating = 'poor'
            
            scores[metric_name] = {
                'value': value,
                'score': round(score, 1),
                'rating': rating,
                'threshold_good': thresholds['good'],
                'threshold_poor': thresholds['needs_improvement']
            }
        
        return scores
    
    def _identify_performance_issues(self, crawl_result, metrics: Dict[str, float]) -> List[Dict[str, Any]]:
        """Identify specific performance issues"""
        issues = []
        
        try:
            html_content = getattr(crawl_result, 'html', '')
            
            # Large images detection
            if metrics.get('image_count', 0) > 10:
                issues.append({
                    'type': 'too_many_images',
                    'severity': 'medium',
                    'impact': 'Slows down page loading',
                    'recommendation': f"Optimize or lazy-load {metrics['image_count']} images",
                    'metric_affected': 'LCP, FCP'
                })
            
            # Individual blocking resources identification
            blocking_issues = self._identify_blocking_resources(html_content)
            issues.extend(blocking_issues)
            
            # Large HTML size
            if metrics.get('content_size', 0) > 100000:  # 100KB
                issues.append({
                    'type': 'large_html',
                    'severity': 'medium',
                    'impact': 'Increases initial download time',
                    'recommendation': f"Reduce HTML size ({metrics['content_size']/1000:.1f}KB). Consider minification.",
                    'metric_affected': 'TTFB, FCP'
                })
            
            # No compression detection
            if not self._has_compression_hints(html_content):
                issues.append({
                    'type': 'no_compression',
                    'severity': 'high',
                    'impact': 'Unnecessarily large resource downloads',
                    'recommendation': 'Enable gzip/brotli compression on server',
                    'metric_affected': 'TTFB, FCP, LCP'
                })
            
            # Layout shift risks
            if metrics.get('cls_risk', 0) > 0.1:
                issues.append({
                    'type': 'layout_shift_risk',
                    'severity': 'high',
                    'impact': 'Potential layout instability',
                    'recommendation': 'Add width/height attributes to images and reserve space for dynamic content',
                    'metric_affected': 'CLS'
                })
            
            # Slow TTFB
            if metrics.get('ttfb', 0) > 600:  # > 600ms
                issues.append({
                    'type': 'slow_ttfb',
                    'severity': 'high',
                    'impact': 'Delays start of page loading',
                    'recommendation': f"Optimize server response time ({metrics['ttfb']:.0f}ms). Consider CDN, caching, or faster hosting.",
                    'metric_affected': 'TTFB, FCP'
                })
            
        except Exception as e:
            logger.error(f"Error identifying performance issues: {str(e)}")
            
        return issues
    
    def _generate_optimization_opportunities(self, metrics: Dict[str, float], crawl_result) -> List[Dict[str, Any]]:
        """Generate specific optimization recommendations"""
        opportunities = []
        
        try:
            # Image optimization
            if metrics.get('image_count', 0) > 0:
                opportunities.append({
                    'category': 'Images',
                    'title': 'Optimize image loading',
                    'description': f"Implement lazy loading for {metrics['image_count']} images",
                    'impact': 'High',
                    'effort': 'Medium',
                    'metrics_improved': ['LCP', 'FCP'],
                    'implementation': 'Add loading="lazy" attribute and consider next-gen formats (WebP, AVIF)'
                })
            
            # JavaScript optimization
            if metrics.get('js_count', 0) > 5:
                opportunities.append({
                    'category': 'JavaScript',
                    'title': 'Optimize JavaScript delivery',
                    'description': f"Defer non-critical JavaScript ({metrics['js_count']} scripts)",
                    'impact': 'High',
                    'effort': 'Medium',
                    'metrics_improved': ['FCP', 'FID'],
                    'implementation': 'Use async/defer attributes and code splitting'
                })
            
            # CSS optimization
            if metrics.get('css_count', 0) > 3:
                opportunities.append({
                    'category': 'CSS',
                    'title': 'Optimize CSS delivery',
                    'description': f"Inline critical CSS and defer non-critical ({metrics['css_count']} stylesheets)",
                    'impact': 'Medium',
                    'effort': 'Medium',
                    'metrics_improved': ['FCP'],
                    'implementation': 'Extract and inline above-the-fold CSS'
                })
            
            # Preloading opportunities
            opportunities.append({
                'category': 'Resource Hints',
                'title': 'Implement resource preloading',
                'description': 'Preload critical resources',
                'impact': 'Medium',
                'effort': 'Low',
                'metrics_improved': ['LCP', 'FCP'],
                'implementation': 'Add <link rel="preload"> for fonts, hero images, and critical CSS'
            })
            
            # Caching opportunities
            opportunities.append({
                'category': 'Caching',
                'title': 'Implement aggressive caching',
                'description': 'Cache static resources with long TTL',
                'impact': 'High',
                'effort': 'Low',
                'metrics_improved': ['TTFB', 'FCP'],
                'implementation': 'Set Cache-Control headers and implement service worker caching'
            })
            
        except Exception as e:
            logger.error(f"Error generating optimization opportunities: {str(e)}")
            
        return opportunities
    
    def _identify_blocking_resources(self, html_content: str) -> List[Dict[str, Any]]:
        """Identify specific blocking CSS and JavaScript resources"""
        blocking_issues = []
        
        if not html_content:
            return blocking_issues
        
        try:
            # Identify blocking CSS files
            css_pattern = r'<link[^>]*rel=["\']stylesheet["\'][^>]*href=["\']([^"\']+)["\'][^>]*(?!media=["\']print["\'])'
            css_matches = re.findall(css_pattern, html_content, re.IGNORECASE)
            
            for css_url in css_matches:
                css_url = clean_url(css_url)  # Clean URL to remove invisible characters
                # Check if CSS is in critical path (not async loaded)
                if not self._is_async_loaded(css_url, html_content):
                    resource_details = ResourceDetailsBuilder.blocking_css(
                        css_url=css_url,
                        load_priority="high",
                        estimated_delay=150.0  # Estimated blocking delay in ms
                    )
                    
                    issue = IssueFactory.create_granular_issue(
                        issue_type='blocking_css_resource',
                        severity='high',
                        category='performance',
                        title='Render-Blocking CSS',
                        description=f'CSS file {self._truncate_url(css_url)} blocks page rendering',
                        recommendation=f'Add media query, preload, or inline critical CSS for {self._get_filename(css_url)}',
                        resource_details=resource_details,
                        score_impact=-3.0  # Impact per blocking resource
                    )
                    blocking_issues.append(issue)
            
            # Identify blocking JavaScript files
            js_pattern = r'<script[^>]*src=["\']([^"\']+)["\'][^>]*(?!async|defer)'
            js_matches = re.findall(js_pattern, html_content, re.IGNORECASE)
            
            for js_url in js_matches:
                js_url = clean_url(js_url)  # Clean URL to remove invisible characters
                # Check if script is in head (more critical blocking)
                in_head = self._is_script_in_head(js_url, html_content)
                severity = 'high' if in_head else 'medium'
                estimated_delay = 200.0 if in_head else 100.0
                
                resource_details = ResourceDetailsBuilder.blocking_javascript(
                    js_url=js_url,
                    has_async=False,
                    has_defer=False,
                    estimated_delay=estimated_delay
                )
                
                issue = IssueFactory.create_granular_issue(
                    issue_type='blocking_js_resource',
                    severity=severity,
                    category='performance',
                    title='Blocking JavaScript',
                    description=f'JavaScript file {self._truncate_url(js_url)} blocks page parsing',
                    recommendation=f'Add async/defer attributes or move {self._get_filename(js_url)} to end of body',
                    resource_details=resource_details,
                    score_impact=-2.5 if in_head else -1.5
                )
                blocking_issues.append(issue)
            
        except Exception as e:
            logger.error(f"Error identifying blocking resources: {str(e)}")
        
        return blocking_issues
    
    def _is_async_loaded(self, resource_url: str, html_content: str) -> bool:
        """Check if CSS resource is loaded asynchronously"""
        # Look for preload patterns or async loading mechanisms
        async_patterns = [
            rf'<link[^>]*rel=["\']preload["\'][^>]*href=["\'][^"\']*{re.escape(resource_url)}[^"\']*["\']',
            rf'loadCSS\(["\'][^"\']*{re.escape(resource_url)}[^"\']*["\']'
        ]
        
        return any(re.search(pattern, html_content, re.IGNORECASE) for pattern in async_patterns)
    
    def _is_script_in_head(self, js_url: str, html_content: str) -> bool:
        """Check if script is loaded in head section"""
        # Extract head section
        head_match = re.search(r'<head[^>]*>(.*?)</head>', html_content, re.DOTALL | re.IGNORECASE)
        if not head_match:
            return False
        
        head_content = head_match.group(1)
        return js_url in head_content
    
    def _truncate_url(self, url: str, max_length: int = 40) -> str:
        """Truncate URL for display purposes"""
        if len(url) <= max_length:
            return url
        return url[:max_length-3] + "..."
    
    def _get_filename(self, url: str) -> str:
        """Extract filename from URL"""
        return url.split('/')[-1].split('?')[0]  # Remove query params
    
    def _has_compression_hints(self, html_content: str) -> bool:
        """Check if content shows signs of compression"""
        # Simple heuristic: uncompressed HTML usually has more whitespace
        # and is generally larger for the same content
        if not html_content:
            return False
            
        # Calculate whitespace ratio
        whitespace_chars = html_content.count(' ') + html_content.count('\n') + html_content.count('\t')
        whitespace_ratio = whitespace_chars / len(html_content) if html_content else 0
        
        # If whitespace ratio is very low, content might be minified/compressed
        # This is a rough heuristic
        return whitespace_ratio < 0.05
    
    def calculate_performance_score(self, cwv_scores: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate overall performance score from Core Web Vitals"""
        if not cwv_scores:
            return {'score': 0, 'rating': 'unknown', 'breakdown': {}}
        
        # Weight different metrics (Google's emphasis)
        weights = {
            'lcp': 0.25,    # High importance
            'fid': 0.25,    # High importance  
            'cls': 0.25,    # High importance
            'fcp': 0.15,    # Medium importance
            'ttfb': 0.10    # Lower importance but still relevant
        }
        
        weighted_score = 0
        total_weight = 0
        breakdown = {}
        
        for metric, weight in weights.items():
            if metric in cwv_scores:
                score_data = cwv_scores[metric]
                weighted_score += score_data['score'] * weight
                total_weight += weight
                breakdown[metric] = {
                    'score': score_data['score'],
                    'rating': score_data['rating'],
                    'weight': weight
                }
        
        # Calculate final score
        final_score = weighted_score / total_weight if total_weight > 0 else 0
        
        # Determine overall rating
        if final_score >= 90:
            rating = 'excellent'
        elif final_score >= 75:
            rating = 'good'
        elif final_score >= 50:
            rating = 'needs_improvement'
        else:
            rating = 'poor'
        
        return {
            'score': round(final_score, 1),
            'rating': rating,
            'breakdown': breakdown,
            'metrics_analyzed': len(breakdown)
        }