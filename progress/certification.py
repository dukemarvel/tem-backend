from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from .models import (
    LessonProgress,
    Certification,
    ScormPackageProgress,
    ScormCertification,
)


@receiver(post_save, sender=LessonProgress)
def award_lesson_certificate(sender, instance, **kwargs):
    if instance.is_completed:
        Certification.objects.get_or_create(
            user=instance.user,
            lesson=instance.lesson,
            defaults={"issued_at": timezone.now()},
        )


@receiver(post_save, sender=ScormPackageProgress)
def award_scorm_certificate(sender, instance, **kwargs):
    # when SCORM progress hits 100%, issue a SCORM cert
    if float(instance.percent) >= 100.0:
        ScormCertification.objects.get_or_create(
            user=instance.user,
            package=instance.package,
            defaults={"issued_at": timezone.now()},
        )
