# teams/tests/test_models.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from courses.models import Course
from teams.models import Organization, TeamMember, BulkPurchase

User = get_user_model()

class ModelsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="admin", email="admin@example.com", password="pass")
        self.org = Organization.objects.create(name="Acme Corp", admin=self.user)
        self.member_user = User.objects.create_user(username="member", email="member@example.com", password="pass")
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

    def test_organization_str(self):
        self.assertEqual(
            str(self.org),
            "Acme Corp (admin: admin@example.com)"
        )

    def test_team_member_str(self):
        expected = "member@example.com in Acme Corp [pending]"
        self.assertEqual(str(self.team_member), expected)

    def test_bulk_purchase_str(self):
        # date formatting YYYY-MM-DD
        date_str = self.bp.purchased_at.strftime("%Y-%m-%d")
        expected = f"5 seats for Acme Corp on {date_str}"
        self.assertEqual(str(self.bp), expected)
