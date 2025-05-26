from django.db import models
from django.conf import settings
from courses.models import Course
from django.db.models import JSONField

class Organization(models.Model):
    name       = models.CharField(max_length=255)
    admin      = models.ForeignKey(settings.AUTH_USER_MODEL,
                                   on_delete=models.CASCADE,
                                   related_name="organizations")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} (admin: {self.admin.email})"


class TeamMember(models.Model):
    PENDING, ACTIVE, REVOKED = "pending", "active", "revoked"
    STATUS_CHOICES = [
        (PENDING,  "Pending"),
        (ACTIVE,   "Active"),
        (REVOKED,  "Revoked"),
    ]

    organization = models.ForeignKey(Organization,
                                     on_delete=models.CASCADE,
                                     related_name="members")
    user         = models.ForeignKey(settings.AUTH_USER_MODEL,
                                     on_delete=models.CASCADE,
                                     related_name="team_memberships")
    invited_by   = models.ForeignKey(settings.AUTH_USER_MODEL,
                                     on_delete=models.SET_NULL,
                                     null=True,
                                     related_name="invited_members")
    status       = models.CharField(max_length=10,
                                    choices=STATUS_CHOICES,
                                    default=PENDING)
    invited_at   = models.DateTimeField(auto_now_add=True)
    joined_at    = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("organization", "user")

    def __str__(self):
        return f"{self.user.email} in {self.organization.name} [{self.status}]"


class BulkPurchase(models.Model):
    organization    = models.ForeignKey(Organization,
                                        on_delete=models.CASCADE,
                                        related_name="purchases")
    purchased_by    = models.ForeignKey(settings.AUTH_USER_MODEL,
                                        on_delete=models.CASCADE)
    seats           = models.PositiveIntegerField()
    courses         = models.ManyToManyField(Course, related_name="team_purchases")
    order_reference = models.CharField(max_length=255)  # tie back to your payments.Order
    purchased_at    = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.seats} seats for {self.organization.name} on {self.purchased_at:%Y-%m-%d}"
    


class TeamAnalyticsSnapshot(models.Model):
    organization     = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="analytics_snapshots"
    )
    snapshot_at      = models.DateTimeField(auto_now_add=True)
    seat_usage       = JSONField()  # {"total_seats":…, "used_seats":…, "pending_invites":…}
    learning_progress = JSONField(
        null=True,
        blank=True
    )  # [ {"user_id":…, "email":…, "completed":…, "total":…, "percent":…}, … ]

    class Meta:
        ordering = ["-snapshot_at"]

    def __str__(self):
        return f"Analytics for {self.organization.name} @ {self.snapshot_at:%Y-%m-%d %H:%M}"
