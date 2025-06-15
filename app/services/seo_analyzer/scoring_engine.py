from typing import List, Dict, Any
from app.core.config import seo_config

class ScoringEngine:
    """Calculates SEO scores based on configurable rules"""
    
    def calculate_page_score(self, issues: List[Dict[str, Any]]) -> float:
        """Calculate overall SEO score for a page based on issues"""
        base_score = 100.0
        
        # Subtract points for each issue
        for issue in issues:
            score_impact = issue.get('score_impact', 0.0)
            base_score += score_impact  # score_impact is negative for issues
        
        # Ensure score doesn't go below 0
        return max(0.0, base_score)
    
    def get_score_category(self, score: float) -> str:
        """Get score category based on score value"""
        if score >= 90:
            return "excellent"
        elif score >= 75:
            return "good"
        elif score >= 50:
            return "needs_improvement"
        else:
            return "poor"
    
    def get_score_color(self, score: float) -> str:
        """Get color representation for score"""
        if score >= 90:
            return "#28a745"  # Green
        elif score >= 75:
            return "#ffc107"  # Yellow
        elif score >= 50:
            return "#fd7e14"  # Orange
        else:
            return "#dc3545"  # Red
    
    def get_priority_issues(self, issues: List[Dict[str, Any]], limit: int = 5) -> List[Dict[str, Any]]:
        """Get the most critical issues that should be fixed first"""
        # Sort by severity and score impact
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        
        sorted_issues = sorted(
            issues,
            key=lambda x: (
                severity_order.get(x.get('severity', 'low'), 3),
                x.get('score_impact', 0.0)  # Lower (more negative) impact first
            )
        )
        
        return sorted_issues[:limit]
    
    def calculate_website_score(self, page_scores: List[float]) -> Dict[str, Any]:
        """Calculate overall website score from individual page scores"""
        if not page_scores:
            return {
                'average_score': 0.0,
                'category': 'poor',
                'pages_analyzed': 0
            }
        
        average_score = sum(page_scores) / len(page_scores)
        
        return {
            'average_score': round(average_score, 2),
            'category': self.get_score_category(average_score),
            'color': self.get_score_color(average_score),
            'pages_analyzed': len(page_scores),
            'min_score': min(page_scores),
            'max_score': max(page_scores)
        }