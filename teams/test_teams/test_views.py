from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from courses.models import Course
from teams.models import Organization, TeamMember, BulkPurchase, TeamAnalyticsSnapshot
from unittest.mock import patch

User = get_user_model()

class TeamsViewsTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            email="admin@org.com", password="pass"
        )
        self.client.force_authenticate(self.admin)
        self.user2 = User.objects.create_user(
             email="user2@org.com", password="pass"
        )
        # create org
        resp = self.client.post(
            "/api/v1/teams/organizations/",
            {"name": "Org Co"}
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.org_id = resp.data["id"]
        self.course = Course.objects.create(
            title="Team Course", description="", price=0, instructor=self.admin
        )

    def test_dashboard_endpoint(self):
        resp = self.client.get(
            f"/api/v1/teams/organizations/{self.org_id}/dashboard/"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["total_seats"], 0)
        self.assertEqual(resp.data["used_seats"], 0)
        self.assertEqual(resp.data["pending_invites"], 0)

    def test_invite_action(self):
        url = f"/api/v1/teams/members/{self.org_id}/invite/"
        resp = self.client.post(url, {"emails": [self.user2.email]}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        invited = resp.data["invited"]
        self.assertEqual(invited[0]["email"], self.user2.email)
        self.assertEqual(invited[0]["status"], TeamMember.PENDING)
        tm = TeamMember.objects.get(organization_id=self.org_id, user=self.user2)
        self.assertEqual(tm.invited_by, self.admin)

    @patch("teams.views.process_team_checkout", return_value="ORDER_XYZ")
    def test_bulk_purchase_create(self, mock_checkout):
        resp = self.client.post(
            "/api/v1/teams/purchases/",
            {"organization": self.org_id, "seats": 2, "courses": [self.course.id]},
            format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data["order_reference"], "ORDER_XYZ")
        mock_checkout.assert_called_once()
        bp = BulkPurchase.objects.get(organization_id=self.org_id)
        self.assertEqual(bp.seats, 2)
        self.assertEqual(bp.purchased_by, self.admin)

    def test_analytics_no_snapshot(self):
        resp = self.client.get(f"/api/v1/teams/organizations/{self.org_id}/analytics/")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(resp.data["detail"], "No analytics snapshot available.")

    def test_analytics_with_snapshot(self):
        snap = TeamAnalyticsSnapshot.objects.create(
            organization=Organization.objects.get(pk=self.org_id),
            seat_usage={"total_seats":1, "used_seats":0, "pending_invites":0},
            learning_progress=[]
        )
        resp = self.client.get(f"/api/v1/teams/organizations/{self.org_id}/analytics/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["seat_usage"], snap.seat_usage)
        self.assertEqual(resp.data["learning_progress"], snap.learning_progress)


class TeamAuthViewsTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_team_register_and_login_flow(self):
        # 1) Register
        payload = {
            "email": "ceo@biz.com",
            "password1": "BizPass123!",
            "password2": "BizPass123!",
            "first_name": "Ceo",
            "last_name": "Boss",
            "company_name": "BizCorp",
            "job_title": "CEO",
            "company_size": 20,
            "team_size": 20,
            "heard_about": "Ad",
            "organizational_needs": "Training"
        }
        resp = self.client.post("/api/v1/teams/register/", payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Ensure org + member created
        user = get_user_model().objects.get(email="ceo@biz.com")
        org = Organization.objects.get(admin=user)
        tm = TeamMember.objects.get(organization=org, user=user)
        self.assertEqual(tm.status, TeamMember.ACTIVE)

        # 2) Login with correct org
        login_payload = {
            "email": "ceo@biz.com",
            "password": "BizPass123!",
            "organization": org.id
        }
        resp2 = self.client.post("/api/v1/teams/login/", login_payload, format="json")
        self.assertEqual(resp2.status_code, status.HTTP_200_OK)
        # tokens present
        self.assertIn("refresh", resp2.data)
        self.assertIn("access", resp2.data)

        # 3) Login fails if not a member
        # create a different user
        other = get_user_model().objects.create_user(
            email="outsider@biz.com",
            password="pass"
        )
        bad_login = {
            "email": "outsider@biz.com",
            "password": "pass",
            "organization": org.id
        }
        resp3 = self.client.post("/api/v1/teams/login/", bad_login, format="json")
        self.assertEqual(resp3.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(resp3.data["detail"], "Not an active member of that team.")