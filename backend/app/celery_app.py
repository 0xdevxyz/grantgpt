"""
Celery application configuration
"""
from celery import Celery
from app.core.config import settings

# Create Celery app
celery_app = Celery(
    "grantgpt",
    broker=f"redis://:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:{settings.REDIS_PORT}/0",
    backend=f"redis://:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:{settings.REDIS_PORT}/0",
    include=["app.tasks", "app.tasks.grant_tasks", "app.tasks.application_tasks", "app.tasks.scraper_tasks"]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Europe/Berlin",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max
    task_soft_time_limit=3000,  # 50 minutes soft limit
    
    # Beat schedule for automated scraping
    beat_schedule={
        # Tier-1 scrapers: Run daily at 2:00 AM
        'run-tier1-scrapers-daily': {
            'task': 'run_tier1_scrapers',
            'schedule': 60 * 60 * 24,  # Every 24 hours
            'options': {'queue': 'scraping'}
        },
        # Tier-2 scrapers: Run weekly on Sunday at 3:00 AM
        'run-tier2-scrapers-weekly': {
            'task': 'run_tier2_scrapers',
            'schedule': 60 * 60 * 24 * 7,  # Every 7 days
            'options': {'queue': 'scraping'}
        },
        # Update embeddings: Run daily at 4:00 AM (after scrapers)
        'update-embeddings-daily': {
            'task': 'update_embeddings',
            'schedule': 60 * 60 * 24,  # Every 24 hours
            'options': {'queue': 'embeddings'}
        },
    },
    
    # Task routing
    task_routes={
        'run_scraper': {'queue': 'scraping'},
        'run_tier1_scrapers': {'queue': 'scraping'},
        'run_tier2_scrapers': {'queue': 'scraping'},
        'update_embeddings': {'queue': 'embeddings'},
        'embed_grants': {'queue': 'embeddings'},
    }
)

