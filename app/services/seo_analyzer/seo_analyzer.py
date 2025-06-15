from typing import Dict, List, Any
import logging

from .crawl4ai_analyzer import Crawl4AIAnalyzer
from .scoring_engine import ScoringEngine
from .issue_detector import IssueDetector

logger = logging.getLogger(__name__)

class SEOAnalyzer:
    def __init__(self):
        self.crawl4ai_analyzer = Crawl4AIAnalyzer()
        self.scoring_engine = ScoringEngine()
        self.issue_detector = IssueDetector()
    
    async def analyze_page_content(self, crawl_result, domain: str) -> Dict[str, Any]:
        """Analyze crawl result from Crawl4AI for SEO factors"""
        try:
            # Use Crawl4AI's extracted content directly
            analysis_result = self.crawl4ai_analyzer.extract_seo_data(crawl_result, domain)
            
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
            
            return issues
            
        except Exception as e:
            logger.error(f"Error detecting issues for {crawl_result.url}: {str(e)}")
            return []