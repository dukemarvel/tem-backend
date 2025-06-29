from django.test import TestCase
from django.contrib.auth import get_user_model
from courses.models import Course
from teams.models import (
    Organization,
    TeamMember,
    BulkPurchase,
    TeamAnalyticsSnapshot,
)

User = get_user_model()

class ModelsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
             email="admin@example.com", password="pass"
        )
        # include extra fields here
        self.org = Organization.objects.create(
            name="Acme Corp",
            admin=self.user,
            company_size=100,
            team_size=10,
            heard_about="Referral",
            organizational_needs="Onboarding"
        )
        self.member_user = User.objects.create_user(
            email="member@example.com", password="pass"
        )
        self.team_member = TeamMember.objects.create(
            organization=self.org,
            user=self.member_user,
            invited_by=self.user,
            status=TeamMember.PENDING
        )
        self.course = Course.objects.create(
            title="Test Course", description="desc", price=0, instructor=self.user
        )
        self.bp = BulkPurchase.objects.create(
            organization=self.org,
            purchased_by=self.user,
            seats=5,
            order_reference="ORD123"
        )
        self.bp.courses.add(self.course)

        self.snapshot = TeamAnalyticsSnapshot.objects.create(
            organization=self.org,
            seat_usage={"total_seats": 5, "used_seats": 1, "pending_invites": 2},
            learning_progress=[{
                "user_id": self.member_user.id,
                "email": self.member_user.email,
                "completed": 1,
                "total": 5,
                "percent": 20
            }]
        )

    def test_organization_str(self):
        self.assertEqual(
            str(self.org),
            "Acme Corp (admin: admin@example.com)"
        )

    def test_organization_extra_fields(self):
        org = self.org
        self.assertEqual(org.company_size, 100)
        self.assertEqual(org.team_size, 10)
        self.assertEqual(org.heard_about, "Referral")
        self.assertEqual(org.organizational_needs, "Onboarding")

    def test_team_member_str(self):
        expected = "member@example.com in Acme Corp [pending]"
        self.assertEqual(str(self.team_member), expected)

    def test_bulk_purchase_str(self):
        date_str = self.bp.purchased_at.strftime("%Y-%m-%d")
        expected = f"5 seats for Acme Corp on {date_str}"
        self.assertEqual(str(self.bp), expected)

    def test_snapshot_str(self):
        date_str = self.snapshot.snapshot_at.strftime("%Y-%m-%d %H:%M")
        expected = f"Analytics for Acme Corp @ {date_str}"
        self.assertEqual(str(self.snapshot), expected)