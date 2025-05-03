from django.db import models
from django.conf import settings
from courses.models import Course

class PaymentTransaction(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("success", "Success"),
        ("failed",  "Failed"),
    ]

    user      = models.ForeignKey(settings.AUTH_USER_MODEL,
                                  on_delete=models.CASCADE,
                                  related_name="payment_transactions")
    course    = models.ForeignKey(Course,
                                  on_delete=models.CASCADE,
                                  related_name="payment_transactions")
    reference = models.CharField(max_length=255, unique=True)
    amount    = models.PositiveIntegerField(
                   help_text="Amount in kobo (lowest currency unit)")
    status    = models.CharField(
                   max_length=20,
                   choices=STATUS_CHOICES,
                   default="pending")
    paid_at   = models.DateTimeField(null=True, blank=True)
    created_at= models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} → {self.course.title} @ {self.reference}"


class Enrollment(models.Model):
    user       = models.ForeignKey(settings.AUTH_USER_MODEL,
                                   on_delete=models.CASCADE,
                                   related_name="enrollments")
    course     = models.ForeignKey(Course,
                                   on_delete=models.CASCADE,
                                   related_name="enrollments")
    enrolled_at= models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "course")

    def __str__(self):
        return f"{self.user.email} enrolled in {self.course.title}"
