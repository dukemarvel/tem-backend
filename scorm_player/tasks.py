from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import ScormPackage
from .upload import handle_scorm_upload

@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
def extract_and_notify(self, package_id):
    """
    1) Unzip & parse the SCORM package.
    2) Notify the instructor on success or failure.
    """
    pkg = ScormPackage.objects.get(pk=package_id)
    try:
        handle_scorm_upload(pkg)
        subject = f"SCORM Package “{pkg.title}” Parsed Successfully"
        msg = "Your SCORM package has been processed and is ready to launch."
    except Exception as e:
        subject = f"Error Parsing SCORM Package “{pkg.title}”"
        msg = f"We encountered an error while processing:\n\n{e}"
        raise  # let Celery retry
    finally:
        send_mail(
            subject,
            msg,
            settings.DEFAULT_FROM_EMAIL,
            [pkg.uploaded_by.email],
            fail_silently=True,
        )
