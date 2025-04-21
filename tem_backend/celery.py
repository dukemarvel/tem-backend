import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tem_backend.settings.development")

app = Celery("tem_backend")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
