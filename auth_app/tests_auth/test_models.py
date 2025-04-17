from django.test import TestCase
from auth_app.models import User, InstructorProfile, StudentProfile

class UserModelTest(TestCase):
    def test_user_str_returns_email(self):
        user = User.objects.create(
            email="user@example.com", username="user1", password="TestPass123!"
        )
        self.assertEqual(str(user), "user@example.com")

    def test_instructorprofile_str(self):
        user = User.objects.create(
            email="instr@example.com", username="instruser", password="TestPass123!"
        )
        instructor = InstructorProfile.objects.create(user=user, bio="Test bio")
        expected_str = f"Instructor: {user.email}"
        self.assertEqual(str(instructor), expected_str)

    def test_studentprofile_str(self):
        user = User.objects.create(
            email="student@example.com", username="studuser", password="TestPass123!"
        )
        student = StudentProfile.objects.create(user=user)
        expected_str = f"Student: {user.email}"
        self.assertEqual(str(student), expected_str)
