from django.db import models
from django.conf import settings
from courses.models import Course


class ScormPackage(models.Model):
    title       = models.CharField(max_length=255)
    course      = models.ForeignKey("courses.Course", on_delete=models.CASCADE, related_name="scorm_packages")
    file        = models.FileField(upload_to="scorm/zips/")
    version     = models.CharField(
        max_length=8,
        choices=[("1.2", "SCORM 1.2"), ("2004", "SCORM 2004")],
        default="1.2",
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="scorm_packages"
    )
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Sco(models.Model):  # single launchable item
    package     = models.ForeignKey(ScormPackage, on_delete=models.CASCADE, related_name="scos")
    identifier  = models.CharField(max_length=255)
    launch_url  = models.CharField(max_length=512)
    title       = models.CharField(max_length=255)
    sequence    = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.package.title} → {self.title}"


class RuntimeData(models.Model):
    user        = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    sco         = models.ForeignKey(Sco, on_delete=models.CASCADE)
    attempt     = models.PositiveIntegerField(default=1)
    data        = models.JSONField(default=dict)       # holds cmi.* key/values
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "sco", "attempt")
