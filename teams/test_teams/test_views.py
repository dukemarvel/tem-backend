from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from courses.models import Course
from teams.models import Organization, TeamMember, BulkPurchase
from unittest.mock import patch

User = get_user_model()

class TeamsViewsTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        # create admin user and log in
        self.admin = User.objects.create_user(username="admin", email="admin@org.com", password="pass")
        self.client.force_authenticate(self.admin)
        # create a normal user for invites
        self.user2 = User.objects.create_user(username="user2", email="user2@org.com", password="pass")
        # create an org
        resp = self.client.post("/api/v1/teams/organizations/", {"name": "Org Co"})
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.org_id = resp.data["id"]
        # add a course
        self.course = Course.objects.create(
            title="Team Course", description="", price=0, instructor=self.admin
        )

    def test_dashboard_endpoint(self):
        # No purchases/members yet
        resp = self.client.get(f"/api/v1/teams/organizations/{self.org_id}/dashboard/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["total_seats"], 0)
        self.assertEqual(resp.data["used_seats"], 0)
        self.assertEqual(resp.data["pending_invites"], 0)

    def test_invite_action(self):
        url = f"/api/v1/teams/members/{self.org_id}/invite/"
        payload = {"emails": [self.user2.email]}
        resp = self.client.post(url, payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        invited = resp.data["invited"]
        self.assertEqual(invited[0]["email"], self.user2.email)
        self.assertEqual(invited[0]["status"], TeamMember.PENDING)
        # verify a TeamMember record exists
        tm = TeamMember.objects.get(organization_id=self.org_id, user=self.user2)
        self.assertEqual(tm.invited_by, self.admin)

    @patch("teams.views.process_team_checkout", return_value="ORDER_XYZ")
    def test_bulk_purchase_create(self, mock_checkout):
        url = "/api/v1/teams/purchases/"
        data = {
            "organization": self.org_id,
            "seats": 2,
            "courses": [self.course.id]
        }
        resp = self.client.post(url, data, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # confirm mocked order_reference was used
        self.assertEqual(resp.data["order_reference"], "ORDER_XYZ")
        mock_checkout.assert_called_once()
        # verify BulkPurchase record
        bp = BulkPurchase.objects.get(organization_id=self.org_id)
        self.assertEqual(bp.seats, 2)
        self.assertEqual(bp.purchased_by, self.admin)
