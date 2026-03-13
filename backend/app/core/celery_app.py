"""Celery application configuration"""
from celery import Celery
from celery.schedules import crontab
from app.config import settings

# Create Celery app
celery_app = Celery(
    "eda_license_dashboard",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=[
        "app.tasks.license_collector",
        "app.tasks.alert_checker",
    ]
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes max per task
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Beat schedule - periodic tasks
celery_app.conf.beat_schedule = {
    'collect-license-data': {
        'task': 'app.tasks.license_collector.collect_all_servers',
        'schedule': 30.0,  # Every 30 seconds
        'options': {'expires': 25}
    },
    'check-alert-rules': {
        'task': 'app.tasks.alert_checker.check_all_alerts',
        'schedule': 60.0,  # Every minute
        'options': {'expires': 55}
    },
    'cleanup-old-data': {
        'task': 'app.tasks.maintenance.cleanup_old_history',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
    },
}

if __name__ == '__main__':
    celery_app.start()
