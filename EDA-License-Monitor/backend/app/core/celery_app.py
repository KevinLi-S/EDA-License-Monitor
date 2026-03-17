from celery import Celery

from app.config import settings

celery_app = Celery(
    'eda_license_dashboard',
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=[
        'app.tasks.collectors',
        'app.tasks.alerts',
        'app.tasks.maintenance',
    ],
)
celery_app.conf.update(
    timezone='Asia/Shanghai',
    task_track_started=True,
    beat_schedule={
        'collect-license-snapshots': {
            'task': 'app.tasks.collectors.collect_license_snapshots',
            'schedule': 30.0,
        },
        'evaluate-alerts': {
            'task': 'app.tasks.alerts.evaluate_alerts',
            'schedule': 60.0,
        },
    },
)
celery_app.autodiscover_tasks(['app.tasks'])
