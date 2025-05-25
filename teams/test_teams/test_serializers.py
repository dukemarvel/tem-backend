from django.test import TestCase
from django.contrib.auth import get_user_model
from courses.models import Course
from teams.models import Organization, TeamMember, BulkPurchase
from teams.serializers import (
    OrganizationSerializer,
    TeamMemberSerializer,
    BulkPurchaseSerializer
)

User = get_user_model()

class SerializersTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user_u", email="u@example.com", password="pass")
        self.org = Organization.objects.create(name="Org", admin=self.user)
        self.member = User.objects.create_user(username="member_m", email="m@example.com", password="pass")
        self.tm = TeamMember.objects.create(
            organization=self.org,
            user=self.member,
            invited_by=self.user
        )
        self.course = Course.objects.create(
            title="C", description="D", price=0, instructor=self.user
        )
        self.bp = BulkPurchase.objects.create(
            organization=self.org,
            purchased_by=self.user,
            seats=3,
            order_reference="REF"
        )
        self.bp.courses.add(self.course)

    def test_organization_serializer_output(self):
        data = OrganizationSerializer(self.org).data
        self.assertEqual(data["id"], self.org.id)
        self.assertEqual(data["name"], "Org")
        self.assertEqual(data["admin"], self.user.id)
        self.assertIn("created_at", data)

    def test_team_member_serializer_output(self):
        data = TeamMemberSerializer(self.tm).data
        self.assertEqual(data["id"], self.tm.id)
        self.assertEqual(data["organization"], self.org.id)
        self.assertEqual(data["user"], self.member.id)
        self.assertIn("status", data)
        self.assertIn("invited_at", data)

    def test_bulk_purchase_serializer_output(self):
        data = BulkPurchaseSerializer(self.bp).data
        self.assertEqual(data["id"], self.bp.id)
        self.assertEqual(data["organization"], self.org.id)
        self.assertEqual(data["seats"], 3)
        self.assertEqual(data["order_reference"], "REF")
        self.assertIn("purchased_at", data)
        # courses should list the PK
        self.assertEqual(data["courses"], [self.course.id])
