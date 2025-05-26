from celery import shared_task
from .models import Organization, TeamAnalyticsSnapshot, TeamMember
from progress.models import LessonProgress 

@shared_task
def snapshot_team_analytics():
    """
    Compute seat & learning metrics for every org and save a snapshot.
    Scheduled to run hourly.
    """
    for org in Organization.objects.all():
        total_seats = sum(p.seats for p in org.purchases.all())
        used_seats = org.members.filter(status=TeamMember.ACTIVE).count()
        pending = org.members.filter(status=TeamMember.PENDING).count()

        # per-user lesson completion
        learning = []
        for member in org.members.filter(status=TeamMember.ACTIVE):
            qs = LessonProgress.objects.filter(user=member.user)
            done = qs.filter(is_completed=True).count()
            total = qs.count()
            learning.append({
                "user_id":   member.user.id,
                "email":     member.user.email,
                "completed": done,
                "total":     total,
                "percent":   (100 * done // total) if total else 0,
            })

        TeamAnalyticsSnapshot.objects.create(
            organization=org,
            seat_usage={
                "total_seats": total_seats,
                "used_seats":  used_seats,
                "pending_invites": pending,
            },
            learning_progress=learning,
        )
