from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import LessonProgress
from scorm_player.models import RuntimeData
from .tasks import recalc_course_progress, recalc_scorm_progress

@receiver(post_save, sender=LessonProgress)
def update_course_progress(sender, instance, **kwargs):
    recalc_course_progress.delay(instance.user_id, instance.lesson.course_id)

@receiver(post_save, sender=RuntimeData)
def update_scorm_package_progress(sender, instance, **kwargs):
    recalc_scorm_progress.delay(instance.user_id, instance.sco.package_id)
