from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from auth_app.models import User, StudentProfile, InstructorProfile

class AuthViewsTest(APITestCase):
    def setUp(self):
        
        self.register_url = reverse("auth_app:auth-register")
        self.login_url = reverse("auth_app:auth-login")
        self.refresh_url = reverse("auth_app:token-refresh")
        self.logout_url = reverse("auth_app:token-blacklist")
        self.me_url = reverse("auth_app:auth-me")
        self.password = "TestPass123!"

    def test_register_student_creates_profile(self):
        data = {
            "email": "student@example.com",
            "username": "studuser",
            "password": self.password,
            "role": "student",
        }
        resp = self.client.post(self.register_url, data, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(email="student@example.com")
        self.assertTrue(hasattr(user, "studentprofile"))
        self.assertFalse(hasattr(user, "instructorprofile"))

    def test_register_instructor_creates_profile(self):
        data = {
            "email": "instr@example.com",
            "username": "instruser",
            "password": self.password,
            "role": "instructor",
        }
        resp = self.client.post(self.register_url, data, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(email="instr@example.com")
        self.assertTrue(hasattr(user, "instructorprofile"))
        self.assertFalse(hasattr(user, "studentprofile"))

    def _create_and_login_user(self, role="student"):
        """
        Helper: Create user and corresponding profile, perform login,
        and return tokens along with the user instance.
        """
        user = User.objects.create_user(
            email="user@example.com", username="user1", password=self.password
        )
        if role == "student":
            StudentProfile.objects.create(user=user)
        else:
            InstructorProfile.objects.create(user=user)

        login_resp = self.client.post(
            self.login_url,
            {"email": user.email, "password": self.password},
            format="json",
        )
        self.assertEqual(login_resp.status_code, status.HTTP_200_OK)
        self.assertIn("access", login_resp.data)
        self.assertIn("refresh", login_resp.data)
        return login_resp.data["access"], login_resp.data["refresh"], user

    def test_login_and_me_endpoint(self):
        access, _, user = self._create_and_login_user(role="student")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        me_resp = self.client.get(self.me_url)
        self.assertEqual(me_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(me_resp.data["email"], user.email)
        self.assertEqual(me_resp.data["role"], "student")

    def test_refresh_token(self):
        _, refresh, _ = self._create_and_login_user()
        refresh_resp = self.client.post(
            self.refresh_url, {"refresh": refresh}, format="json"
        )
        self.assertEqual(refresh_resp.status_code, status.HTTP_200_OK)
        self.assertIn("access", refresh_resp.data)

    def test_logout_blacklists_refresh_token(self):
        _, refresh, _ = self._create_and_login_user()
        logout_resp = self.client.post(
            self.logout_url, {"refresh": refresh}, format="json"
        )
        
        self.assertEqual(logout_resp.status_code, status.HTTP_200_OK)
        # Verify that using the same refresh token results in an error.
        retry_resp = self.client.post(
            self.refresh_url, {"refresh": refresh}, format="json"
        )
        self.assertEqual(retry_resp.status_code, status.HTTP_401_UNAUTHORIZED)
