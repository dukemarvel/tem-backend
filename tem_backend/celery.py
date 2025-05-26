import os
from celery import Celery
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tem_backend.settings.development")

app = Celery("tem_backend")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.conf.timezone = settings.TIME_ZONE
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "snapshot-team-analytics-hourly": {
        "task": "teams.tasks.snapshot_team_analytics",
        "schedule": 3600.0,
    },
}
