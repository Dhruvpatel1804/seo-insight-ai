from celery import Celery

from core.config import settings

celery_app = Celery(
    "app_worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["worker.tasks"],
)

celery_app.conf.timezone = "UTC"

# Beat schedule
celery_app.conf.beat_schedule = {
    "database-healthcheck": {
        "task": "worker.tasks.database_healthcheck",
        "schedule": settings.HEALTHCHECK_INTERVAL_SECONDS,
    },
}
