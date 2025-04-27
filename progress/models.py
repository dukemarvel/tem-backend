from django.conf import settings
from django.db import models
from courses.models import Lesson, Course
from scorm_player.models import ScormPackage
import uuid

User = settings.AUTH_USER_MODEL


class LessonProgress(models.Model):
    user         = models.ForeignKey(User, on_delete=models.CASCADE, related_name="lesson_progress")
    lesson       = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="progress_records")
    is_completed = models.BooleanField(default=False)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "lesson")
        indexes = [models.Index(fields=["user", "lesson"])]


class CourseProgress(models.Model):
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name="course_progress")
    course     = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="progress_records")
    percent    = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "course")
        indexes = [models.Index(fields=["user", "course"])]


class ScormPackageProgress(models.Model):
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name="scorm_progress")
    package    = models.ForeignKey(ScormPackage, on_delete=models.CASCADE, related_name="progress_records")
    percent    = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "package")
        indexes = [models.Index(fields=["user", "package"])]


class Certification(models.Model):
    user      = models.ForeignKey(User, on_delete=models.CASCADE, related_name="certifications")
    lesson    = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="certifications")
    cert_id   = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    issued_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "lesson")
        indexes = [models.Index(fields=["user", "lesson"])]

    def __str__(self):
        return f"{self.user} – Certified on {self.lesson.title}"


class ScormCertification(models.Model):
    user      = models.ForeignKey(User, on_delete=models.CASCADE, related_name="scorm_certifications")
    package   = models.ForeignKey(ScormPackage, on_delete=models.CASCADE, related_name="certifications")
    cert_id   = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    issued_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "package")
        indexes = [models.Index(fields=["user", "package"])]

    def __str__(self):
        return f"{self.user} – SCORM Certified: {self.package.title}"