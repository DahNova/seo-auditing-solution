from typing import Dict, List, Any
import logging

from .crawl4ai_analyzer import Crawl4AIAnalyzer
from .scoring_engine import ScoringEngine
from .issue_detector import IssueDetector
from .performance_analyzer import PerformanceAnalyzer
from .technical_seo_analyzer import TechnicalSEOAnalyzer
from .content.content_quality import ContentQualityAnalyzer
from .content.accessibility import AccessibilityAnalyzer

logger = logging.getLogger(__name__)

class SEOAnalyzer:
    def __init__(self):
        self.crawl4ai_analyzer = Crawl4AIAnalyzer()
        self.scoring_engine = ScoringEngine()
        self.issue_detector = IssueDetector()
        self.performance_analyzer = PerformanceAnalyzer()
        self.technical_seo_analyzer = TechnicalSEOAnalyzer()
        self.content_quality_analyzer = ContentQualityAnalyzer()
        self.accessibility_analyzer = AccessibilityAnalyzer()
    
    async def analyze_page_content(self, crawl_result, domain: str) -> Dict[str, Any]:
        """Analyze crawl result from Crawl4AI for SEO factors"""
        try:
            # Use Crawl4AI's extracted content directly
            analysis_result = self.crawl4ai_analyzer.extract_seo_data(crawl_result, domain)
            
            # Add Core Web Vitals analysis
            performance_data = self.performance_analyzer.analyze_core_web_vitals(crawl_result)
            analysis_result['core_web_vitals'] = performance_data
            
            # Add Technical SEO analysis
            technical_data = self.technical_seo_analyzer.analyze_technical_seo(crawl_result, domain)
            analysis_result['technical_seo'] = technical_data
            
            # Add Content Quality analysis
            content_quality_result = self.content_quality_analyzer.analyze(crawl_result)
            analysis_result['content_quality'] = {
                'scores': content_quality_result.scores,
                'metadata': content_quality_result.metadata
            }
            
            # Add Accessibility analysis
            accessibility_result = self.accessibility_analyzer.analyze(crawl_result)
            analysis_result['accessibility'] = {
                'scores': accessibility_result.scores,
                'metadata': accessibility_result.metadata
            }
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error analyzing page content for {crawl_result.url}: {str(e)}")
            return {}
    
    async def analyze_page_issues(self, crawl_result, page_id: int) -> List[Dict[str, Any]]:
        """Detect and categorize SEO issues for a page using Crawl4AI data"""
        try:
            # Use Crawl4AI extracted data for issue detection
            issues = self.issue_detector.detect_all_issues(
                crawl_result=crawl_result,
                page_id=page_id
            )
            
            # NOTE: Performance issues are now handled by IssueDetector.detect_all_issues()
            # which includes granular blocking resources analysis. No need to duplicate here.
            
            # Add technical SEO issues
            technical_data = self.technical_seo_analyzer.analyze_technical_seo(crawl_result, '')
            technical_issues = technical_data.get('technical_issues', [])
            
            # Convert technical issues to standard issue format
            for tech_issue in technical_issues:
                issues.append({
                    'type': tech_issue['type'],
                    'severity': tech_issue['severity'],
                    'category': tech_issue['category'],
                    'title': tech_issue.get('title', tech_issue['type'].replace('_', ' ').title()),
                    'description': tech_issue['message'],
                    'recommendation': tech_issue['recommendation'],
                    'element': tech_issue.get('impact', ''),
                })
            
            # Add Content Quality issues
            content_quality_result = self.content_quality_analyzer.analyze(crawl_result)
            for cq_issue in content_quality_result.issues:
                issues.append({
                    'type': cq_issue['type'],
                    'severity': cq_issue['severity'],
                    'category': cq_issue['category'],
                    'title': cq_issue['title'],
                    'description': cq_issue['description'],
                    'recommendation': cq_issue['recommendation'],
                    'element': cq_issue.get('element', ''),
                })
            
            # Add Accessibility issues
            accessibility_result = self.accessibility_analyzer.analyze(crawl_result)
            for acc_issue in accessibility_result.issues:
                issues.append({
                    'type': acc_issue['type'],
                    'severity': acc_issue['severity'],
                    'category': acc_issue['category'],
                    'title': acc_issue['title'],
                    'description': acc_issue['description'],
                    'recommendation': acc_issue['recommendation'],
                    'element': acc_issue.get('element', ''),
                })
            
            return issues
            
        except Exception as e:
            logger.error(f"Error detecting issues for {crawl_result.url}: {str(e)}")
            return []
    
    
    def analyze_page(self, crawl_result, domain: str) -> Dict[str, Any]:
        """
        Synchronous wrapper for page analysis - required for enterprise scans
        Combines content analysis and issue detection into a single result
        """
        try:
            # Since we're in sync context, we need to run async methods
            import asyncio
            
            # Check if there's already an event loop running
            try:
                loop = asyncio.get_running_loop()
                # If there's a running loop, we need to create a new one in a thread
                import concurrent.futures
                import threading
                
                def run_analysis():
                    new_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(new_loop)
                    try:
                        # Run content analysis
                        content_result = new_loop.run_until_complete(
                            self.analyze_page_content(crawl_result, domain)
                        )
                        
                        # Run issue detection (using fake page_id for now)
                        issues_result = new_loop.run_until_complete(
                            self.analyze_page_issues(crawl_result, 0)
                        )
                        
                        return content_result, issues_result
                    finally:
                        new_loop.close()
                
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(run_analysis)
                    content_result, issues_result = future.result(timeout=60)
                    
            except RuntimeError:
                # No event loop running, we can create one
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    # Run content analysis
                    content_result = loop.run_until_complete(
                        self.analyze_page_content(crawl_result, domain)
                    )
                    
                    # Run issue detection (using fake page_id for now)
                    issues_result = loop.run_until_complete(
                        self.analyze_page_issues(crawl_result, 0)
                    )
                finally:
                    loop.close()
                    asyncio.set_event_loop(None)
            
            # Combine results
            combined_result = content_result.copy()
            combined_result['issues'] = issues_result
            
            # Calculate scores from the scoring engine
            seo_score = self.scoring_engine.calculate_page_score(issues_result)
            
            # Extract other scores from content analysis
            scores = {
                'seo_score': seo_score,
                'performance_score': content_result.get('core_web_vitals', {}).get('performance_score', 0),
                'technical_score': content_result.get('technical_seo', {}).get('technical_score', 0),
                'mobile_score': content_result.get('mobile_score', 0),
                'content_score': content_result.get('content_quality', {}).get('scores', {}).get('overall_score', 0),
                'accessibility_score': content_result.get('accessibility', {}).get('scores', {}).get('overall_score', 0)
            }
            
            # Add scores to result
            combined_result.update({
                'seo_score': scores.get('seo_score', 0),
                'performance_score': scores.get('performance_score', 0),
                'technical_score': scores.get('technical_score', 0),
                'mobile_score': scores.get('mobile_score', 0),
                'content_score': scores.get('content_score', 0),
                'accessibility_score': scores.get('accessibility_score', 0)
            })
            
            return combined_result
            
        except Exception as e:
            logger.error(f"Error in analyze_page for {crawl_result.url}: {str(e)}")
            return {
                'title': '',
                'meta_description': '',
                'h1_tags': [],
                'h2_tags': [],
                'h3_tags': [],
                'word_count': 0,
                'content_hash': '',
                'seo_score': 0,
                'performance_score': 0,
                'technical_score': 0,
                'mobile_score': 0,
                'content_score': 0,
                'accessibility_score': 0,
                'issues': []
            }