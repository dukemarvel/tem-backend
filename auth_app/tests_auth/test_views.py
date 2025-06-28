from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from auth_app.models import User, StudentProfile, InstructorProfile



class AuthViewsTest(APITestCase):
    def setUp(self):
        self.register_url = reverse("rest_register")
        self.login_url    = reverse("token_obtain_pair")
        self.refresh_url  = reverse("token_refresh")
        self.logout_url   = reverse("rest_logout")
        self.me_url       = reverse("rest_user_details")
        self.password     = "TestPass123!"

    def _create_and_login_user(self, role="student"):
        user = User(email="user@example.com")
        user.set_password(self.password)
        user.save()

        profile_cls = StudentProfile if role == "student" else InstructorProfile
        profile_cls.objects.create(user=user)

        resp = self.client.post(
            self.login_url,
            {"email": user.email, "password": self.password},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        access  = resp.data["access"]
        refresh = resp.data["refresh"]
        return access, refresh, user

    def test_register_student_creates_profile(self):
        resp = self.client.post(
            self.register_url,
            {
                "email": "student@example.com",
                "first_name": "Test",
                "last_name": "Student",
                "password1": self.password,
                "password2": self.password,
                "role": "student",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(email="student@example.com")
        self.assertTrue(hasattr(user, "studentprofile"))
        self.assertFalse(hasattr(user, "instructorprofile"))

    def test_register_instructor_creates_profile(self):
        resp = self.client.post(
            self.register_url,
            {
                "email": "instr@example.com",
                "first_name": "Test",
                "last_name": "Instructor",
                "password1": self.password,
                "password2": self.password,
                "role": "instructor",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(email="instr@example.com")
        self.assertTrue(hasattr(user, "instructorprofile"))
        self.assertFalse(hasattr(user, "studentprofile"))

    def test_login_and_me_endpoint(self):
        access, _, user = self._create_and_login_user(role="student")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        me = self.client.get(self.me_url)
        self.assertEqual(me.status_code, status.HTTP_200_OK)
        self.assertEqual(me.data["email"], user.email)
        self.assertEqual(me.data["role"], "student")

    def test_refresh_token(self):
        _, refresh, _ = self._create_and_login_user()
        resp = self.client.post(self.refresh_url, {"refresh": refresh}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("access", resp.data)

    def test_logout_blacklists_refresh_token(self):
        access, refresh, _ = self._create_and_login_user()

        # authenticate with our access token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

        # call the blacklist endpoint to revoke the refresh token
        blacklist_url = reverse("token_blacklist")
        response = self.client.post(
            blacklist_url,
            {"refresh": refresh},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # now attempting to use the same refresh token must fail
        retry = self.client.post(
            self.refresh_url,
            {"refresh": refresh},
            format="json",
        )
        self.assertEqual(retry.status_code, status.HTTP_401_UNAUTHORIZED)
