"""
Issue Deduplication Service
Prevents duplicate SEO issues from being created during scans
"""
from typing import List, Dict, Any, Set, Tuple
import hashlib
import json
import logging

logger = logging.getLogger(__name__)

class IssueDeduplicator:
    """Handles deduplication of SEO issues during scan processing"""
    
    def __init__(self):
        self.seen_issues: Set[str] = set()
        self.aggregated_issues: Dict[str, Dict[str, Any]] = {}
        
    def create_issue_key(self, issue: Dict[str, Any], page_id: int) -> str:
        """Create a unique key for issue deduplication"""
        # For granular issues with resource details, include resource URL
        element = issue.get('element', '')
        if element and isinstance(element, (dict, str)):
            if isinstance(element, dict):
                resource_url = element.get('resource_url', '')
            else:
                # Try to extract resource URL from JSON string
                try:
                    element_data = json.loads(element) if isinstance(element, str) else element
                    resource_url = element_data.get('resource_url', '') if isinstance(element_data, dict) else ''
                except (json.JSONDecodeError, TypeError):
                    resource_url = ''
            
            # For resource-specific issues, key by page + type + resource
            if resource_url:
                key_data = f"{page_id}:{issue['type']}:{resource_url}"
            else:
                key_data = f"{page_id}:{issue['type']}:{str(element)[:100]}"
        else:
            # For general issues, key by page + type + description excerpt
            description_excerpt = (issue.get('description', '') or '')[:50]
            key_data = f"{page_id}:{issue['type']}:{description_excerpt}"
        
        # Create hash to handle long keys
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def deduplicate_issues(self, issues: List[Dict[str, Any]], page_id: int) -> List[Dict[str, Any]]:
        """
        Deduplicate issues for a specific page
        Returns a list of unique issues with aggregated data where appropriate
        """
        unique_issues = []
        page_seen_keys = set()
        
        for issue in issues:
            issue_key = self.create_issue_key(issue, page_id)
            
            if issue_key not in page_seen_keys:
                # First occurrence of this issue type for this page
                page_seen_keys.add(issue_key)
                unique_issues.append(issue)
                
                logger.debug(f"Added unique issue: {issue['type']} for page {page_id}")
            else:
                # Duplicate detected - this should be rare with proper analyzer logic
                logger.warning(f"Duplicate issue detected and skipped: {issue['type']} on page {page_id}")
        
        return unique_issues
    
    def aggregate_site_wide_duplicates(self, all_issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Aggregate issues that appear frequently across the site
        Updates descriptions to reflect frequency and impact
        """
        # Count occurrences of each issue type + resource combination
        issue_frequency = {}
        issue_examples = {}
        
        for issue in all_issues:
            # Create a site-wide aggregation key (without page_id)
            element = issue.get('element', '')
            if element and isinstance(element, (dict, str)):
                if isinstance(element, dict):
                    resource_url = element.get('resource_url', '')
                else:
                    try:
                        element_data = json.loads(element) if isinstance(element, str) else element
                        resource_url = element_data.get('resource_url', '') if isinstance(element_data, dict) else ''
                    except (json.JSONDecodeError, TypeError):
                        resource_url = ''
                
                if resource_url:
                    agg_key = f"{issue['type']}:{resource_url}"
                else:
                    agg_key = f"{issue['type']}:{str(element)[:50]}"
            else:
                agg_key = f"{issue['type']}:{(issue.get('description', '') or '')[:50]}"
            
            # Count frequency
            if agg_key not in issue_frequency:
                issue_frequency[agg_key] = 0
                issue_examples[agg_key] = issue
            issue_frequency[agg_key] += 1
        
        # Update descriptions for frequently occurring issues
        updated_issues = []
        for issue in all_issues:
            # Determine aggregation key for this issue
            element = issue.get('element', '')
            if element and isinstance(element, (dict, str)):
                if isinstance(element, dict):
                    resource_url = element.get('resource_url', '')
                else:
                    try:
                        element_data = json.loads(element) if isinstance(element, str) else element
                        resource_url = element_data.get('resource_url', '') if isinstance(element_data, dict) else ''
                    except (json.JSONDecodeError, TypeError):
                        resource_url = ''
                
                if resource_url:
                    agg_key = f"{issue['type']}:{resource_url}"
                else:
                    agg_key = f"{issue['type']}:{str(element)[:50]}"
            else:
                agg_key = f"{issue['type']}:{(issue.get('description', '') or '')[:50]}"
            
            frequency = issue_frequency.get(agg_key, 1)
            
            # Clone issue data
            updated_issue = issue.copy()
            
            # Update description and impact for frequently occurring issues
            if frequency > 5:  # Appears on more than 5 pages
                original_desc = updated_issue.get('description', '')
                updated_issue['description'] = f"{original_desc} (Affects {frequency} pages site-wide)"
                
                # Increase score impact for widespread issues
                original_impact = updated_issue.get('score_impact', -1.0)
                updated_issue['score_impact'] = original_impact * min(1.5, 1 + (frequency / 20))
                
                # Escalate severity for very widespread issues
                if frequency > 15 and updated_issue.get('severity') == 'medium':
                    updated_issue['severity'] = 'high'
                    updated_issue['description'] += " (Escalated due to site-wide impact)"
            
            updated_issues.append(updated_issue)
        
        logger.info(f"Processed {len(updated_issues)} issues with frequency analysis")
        return updated_issues
    
    def reset(self):
        """Reset the deduplicator for a new scan"""
        self.seen_issues.clear()
        self.aggregated_issues.clear()