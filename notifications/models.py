from django.db import models
from django.conf import settings

class Notification(models.Model):
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    verb = models.CharField(max_length=255)
    data = models.JSONField(blank=True, null=True)
    link = models.URLField(blank=True, null=True)
    unread = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.recipient.email}: {self.verb}"
