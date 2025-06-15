from celery import Celery
from app.core.config import settings

# Create Celery instance
celery_app = Celery(
    "seo_auditing",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=['app.tasks.scan_tasks', 'app.tasks.monitoring_tasks']
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    
    # Task routing
    task_routes={
        'app.tasks.scan_tasks.run_website_scan': {'queue': 'scans'},
        'app.tasks.monitoring_tasks.check_robots_sitemap': {'queue': 'monitoring'},
    },
    
    # Worker configuration
    worker_max_tasks_per_child=1000,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    
    # Result expiration
    result_expires=3600,
    
    # Retry configuration
    task_default_retry_delay=60,
    task_max_retries=3,
    
    # Rate limiting
    task_default_rate_limit='10/m',
    
    # Beat schedule for periodic tasks
    beat_schedule={
        'check-robots-sitemap-daily': {
            'task': 'app.tasks.monitoring_tasks.check_all_robots_sitemaps',
            'schedule': 86400.0,  # 24 hours
        },
        'scheduled-scans': {
            'task': 'app.tasks.scan_tasks.run_scheduled_scans',
            'schedule': 3600.0,  # 1 hour
        },
    },
    beat_scheduler='django_celery_beat.schedulers:DatabaseScheduler',
)