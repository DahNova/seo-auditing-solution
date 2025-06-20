from typing import Dict, List, Any
import logging

from .crawl4ai_analyzer import Crawl4AIAnalyzer
from .scoring_engine import ScoringEngine
from .issue_detector import IssueDetector
from .performance_analyzer import PerformanceAnalyzer
from .technical_seo_analyzer import TechnicalSEOAnalyzer
from .issue_prioritizer import SmartIssuePrioritizer

logger = logging.getLogger(__name__)

class SEOAnalyzer:
    def __init__(self):
        self.crawl4ai_analyzer = Crawl4AIAnalyzer()
        self.scoring_engine = ScoringEngine()
        self.issue_detector = IssueDetector()
        self.performance_analyzer = PerformanceAnalyzer()
        self.technical_seo_analyzer = TechnicalSEOAnalyzer()
        self.issue_prioritizer = SmartIssuePrioritizer()
    
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
            
            # Add performance issues from Core Web Vitals analysis
            performance_data = self.performance_analyzer.analyze_core_web_vitals(crawl_result)
            performance_issues = performance_data.get('performance_issues', [])
            
            # Convert performance issues to standard issue format
            for perf_issue in performance_issues:
                issues.append({
                    'type': perf_issue['type'],
                    'severity': perf_issue['severity'],
                    'category': 'performance',
                    'title': perf_issue['type'].replace('_', ' ').title(),
                    'description': perf_issue['impact'],
                    'recommendation': perf_issue['recommendation'],
                    'element': perf_issue.get('metric_affected', ''),
                })
            
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