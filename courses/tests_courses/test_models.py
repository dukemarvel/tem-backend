from django.test import TestCase
from django.contrib.auth import get_user_model
from auth_app.models import InstructorProfile
from courses.models import Course, Lesson

User = get_user_model()

class CourseModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="inst@example.com", username="inst", password="pass"
        )
        InstructorProfile.objects.create(user=self.user)
        self.course = Course.objects.create(
            title="Test Course",
            description="A great course",
            price=99.99,
            instructor=self.user,
        )

    def test_str_returns_title_and_email(self):
        self.assertEqual(
            str(self.course),
            "Test Course (by inst@example.com)"
        )

    def test_created_at_auto_now_add(self):
        # created_at should be set on save
        self.assertIsNotNone(self.course.created_at)


class LessonModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="inst2@example.com", username="inst2", password="pass"
        )
        InstructorProfile.objects.create(user=self.user)
        self.course = Course.objects.create(
            title="C2",
            description="Desc2",
            price=10.00,
            instructor=self.user,
        )
        self.lesson = Lesson.objects.create(
            course=self.course,
            title="L1",
            content="Lesson content",
            video_url="http://example.com",
            order=1,
        )

    def test_str_returns_lesson_and_course(self):
        self.assertEqual(
            str(self.lesson),
            "Lesson: L1 in C2"
        )

    def test_defaults_for_optional_fields(self):
        l2 = Lesson.objects.create(
            course=self.course,
            title="L2",
            content="More content"
        )
        # default order is 0 and video_url null
        self.assertEqual(l2.order, 0)
        self.assertIsNone(l2.video_url)

    def test_created_at_auto_now_add(self):
        self.assertIsNotNone(self.lesson.created_at)