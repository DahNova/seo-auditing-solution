"""
Smart Issue Prioritization Engine for SEO Issues
Transforms SEO analysis from basic issue detection to intelligent prioritization
"""

from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import json


class Priority(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Impact(Enum):
    SEVERE = "severe"      # Major ranking impact
    HIGH = "high"          # Significant ranking impact  
    MODERATE = "moderate"  # Moderate ranking impact
    LOW = "low"            # Minor ranking impact


class Effort(Enum):
    MINIMAL = "minimal"    # <1 hour
    LOW = "low"           # 1-4 hours
    MEDIUM = "medium"     # 4-8 hours
    HIGH = "high"         # 1-2 days
    SEVERE = "severe"     # >2 days


@dataclass
class PrioritizedIssue:
    """Enhanced issue with prioritization data"""
    # Original issue data
    category: str
    severity: str
    message: str
    description: str
    recommendation: str
    page_url: str
    element: str = ""
    
    # Prioritization data
    priority: Priority = Priority.MEDIUM
    impact: Impact = Impact.MODERATE
    effort: Effort = Effort.MEDIUM
    priority_score: float = 0.0
    business_impact: str = ""
    urgency_factor: float = 1.0
    
    # Matrix positioning
    matrix_x: float = 0.0  # Impact axis (0-100)
    matrix_y: float = 0.0  # Effort axis (0-100)
    
    # Additional context
    affected_pages_count: int = 1
    potential_traffic_impact: str = ""
    technical_complexity: str = ""


class SmartIssuePrioritizer:
    """
    Advanced issue prioritization system that uses business impact,
    technical complexity, and effort estimation to create actionable
    priority matrices for SEO teams.
    """
    
    def __init__(self):
        self.impact_weights = {
            # Core Web Vitals & Performance
            'core_web_vitals': 0.9,
            'page_speed': 0.8,
            'mobile_performance': 0.85,
            
            # Technical SEO  
            'schema_markup': 0.7,
            'meta_tags': 0.75,
            'technical_seo': 0.8,
            'crawlability': 0.9,
            
            # Content & Structure
            'content_quality': 0.85,
            'heading_structure': 0.6,
            'internal_linking': 0.7,
            
            # Mobile & UX
            'mobile_optimization': 0.8,
            'user_experience': 0.75,
            
            # Security & Trust
            'security': 0.85,
            'accessibility': 0.6,
        }
        
        self.effort_matrix = {
            # Performance issues
            'missing_meta_description': Effort.MINIMAL,
            'missing_title_tag': Effort.MINIMAL,
            'duplicate_meta_tags': Effort.LOW,
            'missing_alt_text': Effort.LOW,
            'broken_internal_links': Effort.MEDIUM,
            'poor_core_web_vitals': Effort.HIGH,
            'missing_schema_markup': Effort.MEDIUM,
            'poor_mobile_optimization': Effort.HIGH,
            'missing_canonical_tags': Effort.LOW,
            'slow_page_load': Effort.HIGH,
            'poor_heading_structure': Effort.MEDIUM,
            'thin_content': Effort.SEVERE,
            'missing_robots_meta': Effort.MINIMAL,
            'no_ssl_certificate': Effort.MEDIUM,
            'missing_sitemap': Effort.LOW,
        }
        
        self.business_impact_templates = {
            Priority.CRITICAL: "Immediate revenue/ranking loss risk",
            Priority.HIGH: "Significant SEO performance impact",
            Priority.MEDIUM: "Moderate improvement opportunity", 
            Priority.LOW: "Minor optimization benefit"
        }
    
    def prioritize_issues(self, issues: List[Dict[str, Any]], 
                         website_context: Dict[str, Any] = None) -> List[PrioritizedIssue]:
        """
        Transform raw SEO issues into prioritized, actionable items
        with business context and effort estimation.
        """
        prioritized_issues = []
        
        for issue_data in issues:
            prioritized_issue = self._create_prioritized_issue(issue_data, website_context)
            prioritized_issues.append(prioritized_issue)
        
        # Sort by priority score (highest first)
        prioritized_issues.sort(key=lambda x: x.priority_score, reverse=True)
        
        return prioritized_issues
    
    def _create_prioritized_issue(self, issue_data: Dict[str, Any], 
                                 context: Dict[str, Any] = None) -> PrioritizedIssue:
        """Create a prioritized issue with smart scoring"""
        
        # Extract basic issue data
        category = issue_data.get('category', 'technical_seo')
        severity = issue_data.get('severity', 'medium')
        message = issue_data.get('message', '')
        description = issue_data.get('description', '')
        recommendation = issue_data.get('recommendation', '')
        page_url = issue_data.get('page_url', '')
        element = issue_data.get('element', '')
        
        # Calculate impact score
        impact = self._calculate_impact(category, severity, message, context)
        
        # Estimate effort required
        effort = self._estimate_effort(category, message, severity)
        
        # Calculate priority score (Impact / Effort ratio with urgency)
        urgency_factor = self._calculate_urgency(category, severity)
        impact_score = self._impact_to_score(impact)
        effort_score = self._effort_to_score(effort)
        
        priority_score = (impact_score / max(effort_score, 0.1)) * urgency_factor
        
        # Determine priority level
        priority = self._score_to_priority(priority_score)
        
        # Calculate matrix positioning
        matrix_x = impact_score  # Impact axis (0-100)
        matrix_y = 100 - effort_score  # Effort axis (inverted - high effort = low Y)
        
        # Generate business impact description
        business_impact = self._generate_business_impact(category, impact, priority)
        
        # Estimate affected pages and traffic impact
        affected_pages = self._estimate_affected_pages(category, context)
        traffic_impact = self._estimate_traffic_impact(impact, affected_pages)
        
        # Technical complexity assessment
        technical_complexity = self._assess_technical_complexity(category, effort)
        
        return PrioritizedIssue(
            category=category,
            severity=severity,
            message=message,
            description=description,
            recommendation=recommendation,
            page_url=page_url,
            element=element,
            priority=priority,
            impact=impact,
            effort=effort,
            priority_score=priority_score,
            business_impact=business_impact,
            urgency_factor=urgency_factor,
            matrix_x=matrix_x,
            matrix_y=matrix_y,
            affected_pages_count=affected_pages,
            potential_traffic_impact=traffic_impact,
            technical_complexity=technical_complexity
        )
    
    def _calculate_impact(self, category: str, severity: str, message: str, 
                         context: Dict[str, Any] = None) -> Impact:
        """Calculate business impact of the issue"""
        
        # Base impact from category weight
        base_weight = self.impact_weights.get(category, 0.5)
        
        # Severity multiplier
        severity_multiplier = {
            'critical': 1.0,
            'high': 0.8,
            'medium': 0.6,
            'low': 0.4
        }.get(severity, 0.5)
        
        # Message-based impact adjustments
        message_lower = message.lower()
        impact_boost = 0.0
        
        if any(term in message_lower for term in ['critical', 'missing', 'broken', 'error']):
            impact_boost += 0.2
        if any(term in message_lower for term in ['core web vitals', 'page speed', 'mobile']):
            impact_boost += 0.3
        if any(term in message_lower for term in ['meta', 'title', 'description']):
            impact_boost += 0.1
        
        # Calculate final impact score
        impact_score = (base_weight * severity_multiplier) + impact_boost
        impact_score = min(impact_score, 1.0)  # Cap at 1.0
        
        # Convert to Impact enum
        if impact_score >= 0.8:
            return Impact.SEVERE
        elif impact_score >= 0.6:
            return Impact.HIGH
        elif impact_score >= 0.4:
            return Impact.MODERATE
        else:
            return Impact.LOW
    
    def _estimate_effort(self, category: str, message: str, severity: str) -> Effort:
        """Estimate effort required to fix the issue"""
        
        # Check predefined effort matrix
        message_lower = message.lower()
        
        # Quick fixes
        if any(term in message_lower for term in ['missing meta', 'missing title', 'missing alt']):
            return Effort.MINIMAL
        
        # Medium complexity fixes
        if any(term in message_lower for term in ['schema', 'canonical', 'robots']):
            return Effort.MEDIUM
        
        # High effort fixes
        if any(term in message_lower for term in ['core web vitals', 'page speed', 'mobile optimization']):
            return Effort.HIGH
        
        # Content-related issues
        if any(term in message_lower for term in ['thin content', 'duplicate content']):
            return Effort.SEVERE
        
        # Default based on severity
        severity_effort_map = {
            'critical': Effort.HIGH,
            'high': Effort.MEDIUM,
            'medium': Effort.LOW,
            'low': Effort.MINIMAL
        }
        
        return severity_effort_map.get(severity, Effort.MEDIUM)
    
    def _calculate_urgency(self, category: str, severity: str) -> float:
        """Calculate urgency multiplier"""
        
        # Critical severity gets high urgency
        if severity == 'critical':
            return 1.5
        
        # Performance issues are urgent
        if category in ['core_web_vitals', 'page_speed', 'mobile_performance']:
            return 1.3
        
        # Technical SEO issues are moderately urgent
        if category in ['technical_seo', 'crawlability']:
            return 1.2
        
        return 1.0
    
    def _impact_to_score(self, impact: Impact) -> float:
        """Convert impact enum to numerical score"""
        impact_scores = {
            Impact.SEVERE: 90,
            Impact.HIGH: 70,
            Impact.MODERATE: 50,
            Impact.LOW: 30
        }
        return impact_scores.get(impact, 50)
    
    def _effort_to_score(self, effort: Effort) -> float:
        """Convert effort enum to numerical score"""
        effort_scores = {
            Effort.MINIMAL: 10,
            Effort.LOW: 25,
            Effort.MEDIUM: 50,
            Effort.HIGH: 75,
            Effort.SEVERE: 90
        }
        return effort_scores.get(effort, 50)
    
    def _score_to_priority(self, score: float) -> Priority:
        """Convert priority score to Priority enum"""
        if score >= 12:
            return Priority.CRITICAL
        elif score >= 8:
            return Priority.HIGH
        elif score >= 4:
            return Priority.MEDIUM
        else:
            return Priority.LOW
    
    def _generate_business_impact(self, category: str, impact: Impact, priority: Priority) -> str:
        """Generate business impact description"""
        
        category_impacts = {
            'core_web_vitals': "Affects Google ranking and user experience directly",
            'page_speed': "Impacts conversion rates and search rankings",
            'mobile_performance': "Critical for mobile-first indexing",
            'schema_markup': "Enhances search result visibility and CTR",
            'meta_tags': "Directly affects search result appearance",
            'technical_seo': "Influences crawlability and indexing",
            'content_quality': "Affects user engagement and rankings",
            'mobile_optimization': "Essential for mobile search performance"
        }
        
        base_impact = category_impacts.get(category, "Affects SEO performance")
        priority_context = self.business_impact_templates.get(priority, "")
        
        return f"{base_impact}. {priority_context}"
    
    def _estimate_affected_pages(self, category: str, context: Dict[str, Any] = None) -> int:
        """Estimate number of pages affected by this issue type"""
        
        if not context:
            return 1
        
        total_pages = context.get('total_pages', 1)
        
        # Site-wide issues
        if category in ['technical_seo', 'meta_tags', 'schema_markup']:
            return max(int(total_pages * 0.7), 1)  # 70% of pages
        
        # Performance issues
        if category in ['core_web_vitals', 'page_speed']:
            return max(int(total_pages * 0.3), 1)  # 30% of pages
        
        return 1
    
    def _estimate_traffic_impact(self, impact: Impact, affected_pages: int) -> str:
        """Estimate potential traffic impact"""
        
        impact_percentages = {
            Impact.SEVERE: (15, 30),
            Impact.HIGH: (8, 15),
            Impact.MODERATE: (3, 8),
            Impact.LOW: (1, 3)
        }
        
        min_impact, max_impact = impact_percentages.get(impact, (1, 3))
        
        if affected_pages > 10:
            return f"Potential {min_impact}-{max_impact}% traffic improvement (site-wide)"
        elif affected_pages > 5:
            return f"Potential {min_impact}-{max_impact}% traffic improvement (multiple pages)"
        else:
            return f"Potential {min_impact}-{max_impact}% traffic improvement (single page)"
    
    def _assess_technical_complexity(self, category: str, effort: Effort) -> str:
        """Assess technical complexity"""
        
        complexity_map = {
            Effort.MINIMAL: "No technical skills required",
            Effort.LOW: "Basic HTML/CMS knowledge",
            Effort.MEDIUM: "Intermediate technical skills",
            Effort.HIGH: "Advanced development required",
            Effort.SEVERE: "Major development project"
        }
        
        return complexity_map.get(effort, "Moderate technical skills")
    
    def generate_priority_matrix_data(self, prioritized_issues: List[PrioritizedIssue]) -> Dict[str, Any]:
        """Generate data for priority matrix visualization"""
        
        matrix_data = {
            'quadrants': {
                'quick_wins': [],      # High Impact, Low Effort
                'major_projects': [],  # High Impact, High Effort  
                'fill_ins': [],        # Low Impact, Low Effort
                'thankless_tasks': []  # Low Impact, High Effort
            },
            'all_issues': [],
            'summary': {
                'total_issues': len(prioritized_issues),
                'critical_issues': 0,
                'high_priority': 0,
                'quick_wins_count': 0,
                'major_projects_count': 0
            }
        }
        
        for issue in prioritized_issues:
            # Classify into quadrants
            high_impact = issue.matrix_x >= 60
            low_effort = issue.matrix_y >= 60  # Remember Y is inverted
            
            if high_impact and low_effort:
                matrix_data['quadrants']['quick_wins'].append(issue)
            elif high_impact and not low_effort:
                matrix_data['quadrants']['major_projects'].append(issue)
            elif not high_impact and low_effort:
                matrix_data['quadrants']['fill_ins'].append(issue)
            else:
                matrix_data['quadrants']['thankless_tasks'].append(issue)
            
            # Add to all issues with matrix positioning
            issue_data = {
                'id': f"{issue.category}_{hash(issue.message) % 10000}",
                'title': issue.message,
                'category': issue.category,
                'priority': issue.priority.value,
                'impact': issue.impact.value,
                'effort': issue.effort.value,
                'x': issue.matrix_x,
                'y': issue.matrix_y,
                'priority_score': round(issue.priority_score, 2),
                'business_impact': issue.business_impact,
                'affected_pages': issue.affected_pages_count,
                'traffic_impact': issue.potential_traffic_impact,
                'technical_complexity': issue.technical_complexity,
                'recommendation': issue.recommendation,
                'page_url': issue.page_url
            }
            matrix_data['all_issues'].append(issue_data)
            
            # Update summary counts
            if issue.priority == Priority.CRITICAL:
                matrix_data['summary']['critical_issues'] += 1
            elif issue.priority == Priority.HIGH:
                matrix_data['summary']['high_priority'] += 1
        
        matrix_data['summary']['quick_wins_count'] = len(matrix_data['quadrants']['quick_wins'])
        matrix_data['summary']['major_projects_count'] = len(matrix_data['quadrants']['major_projects'])
        
        return matrix_data