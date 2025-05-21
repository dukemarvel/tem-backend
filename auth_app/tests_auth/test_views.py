from django.urls import reverse
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase
from auth_app.models import User, StudentProfile, InstructorProfile
from django.conf import settings
import json


patched_rest_auth = {**settings.REST_AUTH, "JWT_AUTH_COOKIE_USE_CSRF": False}


def _dbg(label, resp):
    body = (
        json.dumps(resp.json(), indent=2)
        if resp["Content-Type"].startswith("application/json")
        else "<non-JSON>"
    )
    print(f"\n🔍 {label}: {resp.status_code}\n    body -> {body}")


@override_settings(REST_AUTH=patched_rest_auth)
class AuthViewsTest(APITestCase):
    # ─────────────── set-up ───────────────
    def setUp(self):
        self.register_url = reverse("rest_register")
        self.login_url    = reverse("rest_login")
        self.refresh_url  = reverse("token_refresh")
        self.logout_url   = reverse("rest_logout")
        self.me_url       = reverse("rest_user_details")
        self.password     = "TestPass123!"

    # ─────────────── helper ───────────────
    def _create_and_login_user(self, role="student"):
        user = User.objects.create_user(
            email="user@example.com", username="user1", password=self.password
        )
        (StudentProfile if role == "student" else InstructorProfile).objects.create(user=user)

        resp = self.client.post(
            self.login_url,
            {"email": user.email, "password": self.password},
            format="json",
        )
        #_dbg("LOGIN", resp)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        access  = resp.data["access"]
        refresh = resp.data.get("refresh") or resp.cookies["lms_refresh_token"].value
        self.assertTrue(refresh, "No refresh token found in body or cookie")

        return access, refresh, user

    # ─────────────── tests ────────────────
    def test_register_student_creates_profile(self):
        resp = self.client.post(
            self.register_url,
            {
                "email": "student@example.com",
                "username": "studuser",
                "password1": self.password,
                "password2": self.password,
                "role": "student",
            },
            format="json",
        )
        #_dbg("REGISTER-student", resp)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(email="student@example.com")
        self.assertTrue(hasattr(user, "studentprofile"))
        self.assertFalse(hasattr(user, "instructorprofile"))

    def test_register_instructor_creates_profile(self):
        resp = self.client.post(
            self.register_url,
            {
                "email": "instr@example.com",
                "username": "instruser",
                "password1": self.password,
                "password2": self.password,
                "role": "instructor",
            },
            format="json",
        )
        #_dbg("REGISTER-instr", resp)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(email="instr@example.com")
        self.assertTrue(hasattr(user, "instructorprofile"))
        self.assertFalse(hasattr(user, "studentprofile"))

    def test_login_and_me_endpoint(self):
        access, _, user = self._create_and_login_user(role="student")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        me = self.client.get(self.me_url)
        #_dbg("ME", me)
        self.assertEqual(me.status_code, status.HTTP_200_OK)
        self.assertEqual(me.data["email"], user.email)
        self.assertEqual(me.data["role"], "student")

    def test_refresh_token(self):
        _, refresh, _ = self._create_and_login_user()
        resp = self.client.post(self.refresh_url, {"refresh": refresh}, format="json")
        #_dbg("REFRESH", resp)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("access", resp.data)

    def test_logout_blacklists_refresh_token(self):
        access, refresh, _ = self._create_and_login_user()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

        logout = self.client.post(self.logout_url, {"refresh": refresh}, format="json")
        #_dbg("LOGOUT", logout)

        retry = self.client.post(self.refresh_url, {"refresh": refresh}, format="json")
        #_dbg("REFRESH-retry", retry)
        self.assertEqual(retry.status_code, status.HTTP_401_UNAUTHORIZED)
