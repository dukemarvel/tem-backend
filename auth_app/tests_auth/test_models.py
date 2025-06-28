from django.test import TestCase
from auth_app.models import User, InstructorProfile, StudentProfile

class UserModelTest(TestCase):
    def test_user_str_returns_email(self):
        user = User(email="user@example.com")
        user.set_password("TestPass123!")
        user.save()
        self.assertEqual(str(user), "user@example.com")

    def test_instructorprofile_str(self):
        user = User(email="instr@example.com")
        user.set_password("TestPass123!")
        user.save()
        instructor = InstructorProfile.objects.create(user=user, bio="Test bio")
        expected_str = f"Instructor: {user.email}"
        self.assertEqual(str(instructor), expected_str)

    def test_studentprofile_str(self):
        user = User(email="student@example.com")
        user.set_password("TestPass123!")
        user.save()
        student = StudentProfile.objects.create(user=user)
        expected_str = f"Student: {user.email}"
        self.assertEqual(str(student), expected_str)
