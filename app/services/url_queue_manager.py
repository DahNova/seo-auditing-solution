"""
Enterprise URL Queue Manager
Priority-based URL queue with intelligent scoring, crawl budget management,
and enterprise-scale URL processing for SEO auditing.
"""
import logging
import asyncio
from typing import List, Dict, Any, Optional, Set, Iterator
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import heapq
import json
from collections import defaultdict
import hashlib

from .url_discovery_service import DiscoveredURL, URLSource
from app.services.url_utils import normalize_url

logger = logging.getLogger(__name__)

class QueuePriority(Enum):
    """Queue priority levels for URL processing"""
    CRITICAL = 1.0    # Homepage, critical pages
    HIGH = 0.8        # Important pages, sitemap priority > 0.8
    MEDIUM = 0.6      # Normal pages, sitemap priority 0.4-0.8
    LOW = 0.4         # Low priority pages, depth > 3
    DEFERRED = 0.2    # Background processing, very low priority

class ProcessingStatus(Enum):
    """URL processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    RETRY = "retry"

@dataclass
class QueuedURL:
    """Represents a URL in the processing queue with metadata"""
    url: str
    priority: float
    discovered_url: DiscoveredURL
    queue_priority: QueuePriority
    
    # Processing metadata
    status: ProcessingStatus = ProcessingStatus.PENDING
    queued_at: datetime = field(default_factory=datetime.now)
    processing_started: Optional[datetime] = None
    processing_completed: Optional[datetime] = None
    
    # Retry and error handling
    retry_count: int = 0
    max_retries: int = 3
    last_error: Optional[str] = None
    
    # Performance tracking
    estimated_processing_time: int = 30  # seconds
    actual_processing_time: Optional[int] = None
    
    # Dependencies and constraints
    depends_on: List[str] = field(default_factory=list)  # URLs that must be processed first
    processing_group: Optional[str] = None  # Group for batch processing
    
    def __lt__(self, other):
        """Enable heapq operations (higher priority = lower number for min-heap)"""
        return self.priority > other.priority  # Reverse for max-heap behavior
    
    @property
    def should_retry(self) -> bool:
        """Check if URL should be retried"""
        return (self.status == ProcessingStatus.FAILED and 
                self.retry_count < self.max_retries)
    
    @property
    def processing_duration(self) -> Optional[int]:
        """Get processing duration in seconds"""
        if self.processing_started and self.processing_completed:
            return int((self.processing_completed - self.processing_started).total_seconds())
        return None

class CrawlBudget:
    """Manages crawl budget allocation and tracking"""
    
    def __init__(self, total_budget: int = 1000, time_budget: int = 3600):
        self.total_budget = total_budget  # Maximum URLs to process
        self.time_budget = time_budget    # Maximum time in seconds
        self.used_budget = 0
        self.start_time = datetime.now()
        
        # Priority allocation percentages
        self.priority_allocation = {
            QueuePriority.CRITICAL: 0.3,   # 30% of budget
            QueuePriority.HIGH: 0.4,       # 40% of budget
            QueuePriority.MEDIUM: 0.2,     # 20% of budget
            QueuePriority.LOW: 0.1,        # 10% of budget
            QueuePriority.DEFERRED: 0.0    # Only if budget remains
        }
        
        self.priority_used = {priority: 0 for priority in QueuePriority}
    
    def can_process(self, priority: QueuePriority) -> bool:
        """Check if we can process a URL with given priority"""
        # Check total budget
        if self.used_budget >= self.total_budget:
            return False
        
        # Check time budget
        elapsed = (datetime.now() - self.start_time).total_seconds()
        if elapsed >= self.time_budget:
            return False
        
        # Check priority-specific allocation
        allocated = int(self.total_budget * self.priority_allocation[priority])
        if allocated > 0 and self.priority_used[priority] >= allocated:
            # Check if we can use unused budget from other priorities
            total_used = sum(self.priority_used.values())
            if total_used >= self.total_budget:
                return False
        
        return True
    
    def consume(self, priority: QueuePriority, amount: int = 1):
        """Consume budget for processing"""
        self.used_budget += amount
        self.priority_used[priority] += amount
    
    @property
    def remaining_budget(self) -> int:
        """Get remaining crawl budget"""
        return max(0, self.total_budget - self.used_budget)
    
    @property
    def remaining_time(self) -> int:
        """Get remaining time budget in seconds"""
        elapsed = (datetime.now() - self.start_time).total_seconds()
        return max(0, int(self.time_budget - elapsed))

class URLQueueManager:
    """Enterprise URL queue manager with priority-based processing"""
    
    def __init__(self, crawl_budget: CrawlBudget = None):
        self.crawl_budget = crawl_budget or CrawlBudget()
        
        # Priority queues (using heapq for efficient priority sorting)
        self.queues = {
            priority: [] for priority in QueuePriority
        }
        
        # URL tracking
        self.url_map: Dict[str, QueuedURL] = {}
        self.processed_urls: Set[str] = set()
        self.failed_urls: Set[str] = set()
        
        # Processing statistics
        self.stats = {
            'total_queued': 0,
            'total_processed': 0,
            'total_failed': 0,
            'total_skipped': 0,
            'processing_rate': 0.0,  # URLs per second
            'average_processing_time': 0.0,
            'queue_depths': {priority.name: 0 for priority in QueuePriority},
            'priority_distribution': {priority.name: 0 for priority in QueuePriority}
        }
        
        # Concurrency control
        self.max_concurrent = 10
        self.processing_semaphore = asyncio.Semaphore(self.max_concurrent)
        self.currently_processing: Set[str] = set()
    
    def add_urls(self, discovered_urls: List[DiscoveredURL]) -> Dict[str, int]:
        """Add discovered URLs to the appropriate priority queues"""
        added_counts = {priority.name: 0 for priority in QueuePriority}
        skipped_count = 0
        
        for discovered_url in discovered_urls:
            # Skip if already processed or in queue
            if (discovered_url.url in self.processed_urls or 
                discovered_url.url in self.url_map):
                skipped_count += 1
                continue
            
            # Determine queue priority based on URL characteristics
            queue_priority = self._determine_queue_priority(discovered_url)
            
            # Create queued URL
            queued_url = QueuedURL(
                url=discovered_url.url,
                priority=discovered_url.calculated_priority,
                discovered_url=discovered_url,
                queue_priority=queue_priority,
                estimated_processing_time=self._estimate_processing_time(discovered_url)
            )
            
            # Add to appropriate queue
            heapq.heappush(self.queues[queue_priority], queued_url)
            self.url_map[discovered_url.url] = queued_url
            
            # Update statistics
            added_counts[queue_priority.name] += 1
            self.stats['total_queued'] += 1
            self.stats['queue_depths'][queue_priority.name] += 1
            self.stats['priority_distribution'][queue_priority.name] += 1
        
        logger.info(f"Added URLs to queue: {sum(added_counts.values())} new, {skipped_count} skipped")
        return added_counts
    
    def _determine_queue_priority(self, discovered_url: DiscoveredURL) -> QueuePriority:
        """Determine appropriate queue priority for a discovered URL"""
        priority = discovered_url.calculated_priority
        
        # Critical priority for very important URLs
        if priority >= 0.9 or discovered_url.source == URLSource.MANUAL:
            return QueuePriority.CRITICAL
        
        # High priority for sitemap URLs with high priority
        elif priority >= 0.7:
            return QueuePriority.HIGH
        
        # Medium priority for normal URLs
        elif priority >= 0.4:
            return QueuePriority.MEDIUM
        
        # Low priority for deep or less important URLs
        elif priority >= 0.2:
            return QueuePriority.LOW
        
        # Deferred for very low priority URLs
        else:
            return QueuePriority.DEFERRED
    
    def _estimate_processing_time(self, discovered_url: DiscoveredURL) -> int:
        """Estimate processing time for a URL based on characteristics"""
        base_time = 30  # Base 30 seconds
        
        # Adjust based on source
        if discovered_url.source == URLSource.SITEMAP:
            base_time += 10  # Sitemap URLs might be more complex
        
        # Adjust based on depth
        base_time += discovered_url.depth * 5
        
        # Adjust based on URL patterns
        if any(pattern in discovered_url.url.lower() for pattern in ['blog', 'news', 'article']):
            base_time += 15  # Content pages take longer
        
        return min(base_time, 180)  # Cap at 3 minutes
    
    async def get_next_batch(self, batch_size: int = 10) -> List[QueuedURL]:
        """Get next batch of URLs to process, respecting priority and budget"""
        batch = []
        
        # Process queues in priority order
        for priority in QueuePriority:
            if len(batch) >= batch_size:
                break
            
            queue = self.queues[priority]
            
            while queue and len(batch) < batch_size:
                if not self.crawl_budget.can_process(priority):
                    break
                
                # Get highest priority URL from this queue
                try:
                    queued_url = heapq.heappop(queue)
                    
                    # Skip if already processing or processed
                    if (queued_url.url in self.currently_processing or 
                        queued_url.url in self.processed_urls):
                        continue
                    
                    # Check dependencies
                    if self._dependencies_satisfied(queued_url):
                        batch.append(queued_url)
                        self.currently_processing.add(queued_url.url)
                        queued_url.status = ProcessingStatus.PROCESSING
                        queued_url.processing_started = datetime.now()
                        
                        # Consume budget
                        self.crawl_budget.consume(priority)
                        self.stats['queue_depths'][priority.name] -= 1
                    else:
                        # Put back in queue if dependencies not satisfied
                        heapq.heappush(queue, queued_url)
                        break
                
                except IndexError:
                    break  # Queue is empty
        
        return batch
    
    def _dependencies_satisfied(self, queued_url: QueuedURL) -> bool:
        """Check if all dependencies for a URL are satisfied"""
        for dep_url in queued_url.depends_on:
            if dep_url not in self.processed_urls:
                return False
        return True
    
    async def mark_completed(self, url: str, success: bool = True, error: str = None):
        """Mark a URL as completed or failed"""
        if url not in self.url_map:
            logger.warning(f"Attempted to mark unknown URL as completed: {url}")
            return
        
        queued_url = self.url_map[url]
        queued_url.processing_completed = datetime.now()
        
        if success:
            queued_url.status = ProcessingStatus.COMPLETED
            self.processed_urls.add(url)
            self.stats['total_processed'] += 1
        else:
            queued_url.status = ProcessingStatus.FAILED
            queued_url.last_error = error
            queued_url.retry_count += 1
            
            if queued_url.should_retry:
                # Re-queue for retry
                queued_url.status = ProcessingStatus.RETRY
                heapq.heappush(self.queues[queued_url.queue_priority], queued_url)
                self.stats['queue_depths'][queued_url.queue_priority.name] += 1
                logger.info(f"Re-queued {url} for retry ({queued_url.retry_count}/{queued_url.max_retries})")
            else:
                self.failed_urls.add(url)
                self.stats['total_failed'] += 1
        
        # Update processing time statistics
        if queued_url.processing_duration:
            queued_url.actual_processing_time = queued_url.processing_duration
            self._update_processing_stats(queued_url.actual_processing_time)
        
        # Remove from currently processing
        self.currently_processing.discard(url)
    
    def _update_processing_stats(self, processing_time: int):
        """Update processing time statistics"""
        # Simple moving average for processing rate
        if self.stats['total_processed'] > 0:
            current_avg = self.stats['average_processing_time']
            new_avg = ((current_avg * (self.stats['total_processed'] - 1)) + processing_time) / self.stats['total_processed']
            self.stats['average_processing_time'] = new_avg
            
            # Calculate processing rate (URLs per second)
            self.stats['processing_rate'] = 1.0 / new_avg if new_avg > 0 else 0.0
    
    def get_queue_status(self) -> Dict[str, Any]:
        """Get comprehensive queue status"""
        total_pending = sum(len(queue) for queue in self.queues.values())
        
        status = {
            'total_pending': total_pending,
            'total_processing': len(self.currently_processing),
            'total_processed': len(self.processed_urls),
            'total_failed': len(self.failed_urls),
            'crawl_budget': {
                'remaining': self.crawl_budget.remaining_budget,
                'remaining_time': self.crawl_budget.remaining_time,
                'used': self.crawl_budget.used_budget,
                'total': self.crawl_budget.total_budget
            },
            'queue_depths': {
                priority.name: len(self.queues[priority]) 
                for priority in QueuePriority
            },
            'processing_stats': self.stats.copy(),
            'estimated_completion_time': self._estimate_completion_time()
        }
        
        return status
    
    def _estimate_completion_time(self) -> Optional[str]:
        """Estimate time to complete all pending URLs"""
        total_pending = sum(len(queue) for queue in self.queues.values())
        
        if total_pending == 0:
            return "0 minutes"
        
        if self.stats['average_processing_time'] > 0:
            avg_time = self.stats['average_processing_time']
            total_time = total_pending * avg_time / self.max_concurrent
            
            if total_time < 60:
                return f"{int(total_time)} seconds"
            elif total_time < 3600:
                return f"{int(total_time / 60)} minutes"
            else:
                return f"{int(total_time / 3600)} hours"
        
        return "Unknown"
    
    def get_priority_queue_iterator(self, priority: QueuePriority) -> Iterator[QueuedURL]:
        """Get iterator for a specific priority queue"""
        # Create a copy of the queue for iteration
        queue_copy = self.queues[priority].copy()
        
        while queue_copy:
            yield heapq.heappop(queue_copy)
    
    def rebalance_queues(self):
        """Rebalance queues based on current priorities and budget"""
        logger.info("Rebalancing URL queues")
        
        # Get all pending URLs
        all_pending = []
        for priority in QueuePriority:
            while self.queues[priority]:
                all_pending.append(heapq.heappop(self.queues[priority]))
        
        # Re-evaluate priorities and re-queue
        for queued_url in all_pending:
            # Recalculate priority based on current conditions
            new_priority = self._determine_queue_priority(queued_url.discovered_url)
            queued_url.queue_priority = new_priority
            
            # Update queue placement
            heapq.heappush(self.queues[new_priority], queued_url)
        
        # Update statistics
        self.stats['queue_depths'] = {
            priority.name: len(self.queues[priority]) 
            for priority in QueuePriority
        }
        
        logger.info("Queue rebalancing completed")
    
    def export_queue_state(self) -> Dict[str, Any]:
        """Export current queue state for persistence or analysis"""
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'crawl_budget': {
                'total_budget': self.crawl_budget.total_budget,
                'used_budget': self.crawl_budget.used_budget,
                'time_budget': self.crawl_budget.time_budget,
                'start_time': self.crawl_budget.start_time.isoformat()
            },
            'queue_depths': {
                priority.name: len(self.queues[priority]) 
                for priority in QueuePriority
            },
            'statistics': self.stats.copy(),
            'processed_urls': list(self.processed_urls),
            'failed_urls': list(self.failed_urls),
            'currently_processing': list(self.currently_processing)
        }
        
        return export_data
    
    def clear_completed_urls(self):
        """Clear processed URLs to free memory (for long-running processes)"""
        completed_count = len(self.processed_urls)
        failed_count = len(self.failed_urls)
        
        # Remove completed URLs from tracking
        completed_urls = set()
        for url in list(self.url_map.keys()):
            queued_url = self.url_map[url]
            if queued_url.status in [ProcessingStatus.COMPLETED, ProcessingStatus.FAILED]:
                completed_urls.add(url)
                del self.url_map[url]
        
        # Keep sets for duplicate checking but could be optimized further
        logger.info(f"Cleared {len(completed_urls)} completed URLs from memory")
        
        return {
            'cleared_count': len(completed_urls),
            'remaining_in_memory': len(self.url_map)
        }