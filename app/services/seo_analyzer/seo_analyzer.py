from typing import Dict, List, Any
import logging

from .crawl4ai_analyzer import Crawl4AIAnalyzer
from .scoring_engine import ScoringEngine
from .issue_detector import IssueDetector
from .performance_analyzer import PerformanceAnalyzer
from .technical_seo_analyzer import TechnicalSEOAnalyzer
from .issue_prioritizer import SmartIssuePrioritizer
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
        self.issue_prioritizer = SmartIssuePrioritizer()
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
    
    async def prioritize_scan_issues(self, all_issues: List[Dict[str, Any]], 
                                   website_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Apply smart prioritization to all issues from a scan
        Returns prioritized issues with visual matrix data
        """
        try:
            # Prepare issues for prioritization
            issues_for_prioritization = []
            
            for issue in all_issues:
                issue_data = {
                    'category': issue.get('category', 'technical_seo'),
                    'severity': issue.get('severity', 'medium'),
                    'message': issue.get('message', ''),
                    'description': issue.get('description', ''),
                    'recommendation': issue.get('recommendation', ''),
                    'page_url': issue.get('page_url', ''),
                    'element': issue.get('affected_element', '')
                }
                issues_for_prioritization.append(issue_data)
            
            # Apply smart prioritization
            prioritized_issues = self.issue_prioritizer.prioritize_issues(
                issues_for_prioritization, 
                website_context
            )
            
            # Generate priority matrix data for visualization
            matrix_data = self.issue_prioritizer.generate_priority_matrix_data(prioritized_issues)
            
            return {
                'prioritized_issues': prioritized_issues,
                'priority_matrix': matrix_data,
                'summary': {
                    'total_issues': len(prioritized_issues),
                    'critical_count': len([i for i in prioritized_issues if i.priority.value == 'critical']),
                    'high_count': len([i for i in prioritized_issues if i.priority.value == 'high']),
                    'quick_wins_count': len(matrix_data['quadrants']['quick_wins']),
                    'major_projects_count': len(matrix_data['quadrants']['major_projects'])
                }
            }
            
        except Exception as e:
            logger.error(f"Error prioritizing issues: {str(e)}")
            return {
                'prioritized_issues': [],
                'priority_matrix': {'quadrants': {}, 'all_issues': [], 'summary': {}},
                'summary': {'total_issues': 0, 'critical_count': 0, 'high_count': 0, 'quick_wins_count': 0, 'major_projects_count': 0}
            }