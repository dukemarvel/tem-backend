from celery import shared_task
from courses.models import Lesson
from scorm_player.models import Sco, RuntimeData
from .models import (
    LessonProgress,
    CourseProgress,
    ScormPackageProgress
)


@shared_task
def recalc_course_progress(user_id, course_id):
    total = Lesson.objects.filter(course_id=course_id).count()
    completed = LessonProgress.objects.filter(
        user_id=user_id,
        lesson__course_id=course_id,
        is_completed=True
    ).count()
    percent = (completed / total * 100) if total else 0
    cp, _ = CourseProgress.objects.get_or_create(
        user_id=user_id, course_id=course_id
    )
    cp.percent = round(percent, 2)
    cp.save()


@shared_task
def recalc_scorm_progress(user_id, package_id):
    total = Sco.objects.filter(package_id=package_id).count()
    # consider a SCO completed if RuntimeData.data carries a “completed” or “passed” status
    completed = 0
    for rd in RuntimeData.objects.filter(user_id=user_id, sco__package_id=package_id):
        status = (
            rd.data.get("cmi.core.lesson_status")
            or rd.data.get("cmi.success_status")
            or rd.data.get("cmi.completion_status")
        )
        if status in {"completed", "passed"}:
            completed += 1

    percent = (completed / total * 100) if total else 0
    sp, _ = ScormPackageProgress.objects.get_or_create(
        user_id=user_id, package_id=package_id
    )
    sp.percent = round(percent, 2)
    sp.save()
