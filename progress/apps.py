from django.apps import AppConfig


class ProgressConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'progress'

    def ready(self):
        # import signals so they’re registered
        import progress.signals
        import progress.certification