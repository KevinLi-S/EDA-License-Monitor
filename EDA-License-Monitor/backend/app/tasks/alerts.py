from app.core.celery_app import celery_app


@celery_app.task(name='app.tasks.alerts.evaluate_alerts')
def evaluate_alerts() -> dict:
    return {'status': 'queued', 'message': 'phase-1 alert evaluation skeleton'}
