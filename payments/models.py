from django.db import models
from django.conf import settings
from courses.models import Course
from teams.models import Organization
from django.utils import timezone

class BulkPaymentTransaction(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("success", "Success"),
        ("failed",  "Failed"),
    ]

    organization   = models.ForeignKey(Organization, on_delete=models.CASCADE)
    user           = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    seats          = models.PositiveIntegerField()
    courses        = models.ManyToManyField(Course)
    reference      = models.CharField(max_length=255, unique=True)
    amount         = models.PositiveIntegerField(help_text="in kobo")
    status         = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    paid_at        = models.DateTimeField(null=True, blank=True)
    created_at     = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.organization.name} [{self.reference}] → ₦{self.amount/100:.2f}"

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

    # NEW —
    access_expires = models.DateTimeField(
        null=True, blank=True,
        help_text="Null = lifetime. Otherwise access ends at this timestamp."
    )

    @property
    def is_active(self) -> bool:
        """
        True  → lifetime OR not-yet-expired
        False → expired (and time-limited)
        """
        return (
            self.access_expires is None
            or self.access_expires > timezone.now()
        )

    class Meta:
        unique_together = ("user", "course")

    def __str__(self):
        return f"{self.user.email} enrolled in {self.course.title}"
