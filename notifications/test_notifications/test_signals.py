from django.test import TestCase
from django.contrib.auth import get_user_model
from allauth.account.signals import user_signed_up
from unittest.mock import patch

from notifications.models import Notification
from notifications import tasks
from payments.models import Enrollment
from courses.models import Course, Lesson
from progress.models import LessonProgress, CourseProgress

User = get_user_model()

class NotificationSignalsTest(TestCase):
    def setUp(self):
        # one instructor, one student, one course
        self.instructor = User.objects.create_user(
            username="instructor", email="inst@example.com", password="pass"
        )
        self.student = User.objects.create_user(
            username="student", email="stud@example.com", password="pass"
        )
        self.course = Course.objects.create(
            title="Demo Course",
            description="Desc",
            price=0,
            instructor=self.instructor,
        )

    @patch.object(tasks.send_notification_email, "delay")
    def test_welcome_user_signal(self, mock_delay):
        new_user = User.objects.create_user(
            username="newbie", email="new@example.com", password="pass"
        )
        user_signed_up.send(sender=None, request=None, user=new_user)

        notif = Notification.objects.filter(recipient=new_user).first()
        self.assertIsNotNone(notif)
        self.assertIn("Welcome", notif.verb)

        mock_delay.assert_called_once_with(
            new_user.email,
            "Welcome to Acadamier!",
            f"Hi {new_user.username}, welcome aboard! 🎉"
        )

    @patch.object(tasks.send_notification_email, "delay")
    def test_enrollment_creates_notification(self, mock_delay):
        Enrollment.objects.create(user=self.student, course=self.course)

        notif = Notification.objects.filter(
            recipient=self.student,
            verb__startswith="You’re now enrolled in"
        ).first()
        self.assertIsNotNone(notif)

        mock_delay.assert_called_once()
        args, _ = mock_delay.call_args
        self.assertIn(self.course.title, args[1])  # subject contains course title

    @patch.object(tasks.send_notification_email, "delay")
    def test_lesson_progress_notification(self, mock_delay):
        Lesson.objects.create(course=self.course, title="L1", content="", order=1)
        lesson2 = Lesson.objects.create(course=self.course, title="L2", content="", order=2)

        LessonProgress.objects.create(
            user=self.student, lesson=lesson2, is_completed=True
        )

        notif = Notification.objects.filter(
            recipient=self.student,
            verb__contains="completed"
        ).first()
        self.assertIsNotNone(notif)
        mock_delay.assert_called_once()

    @patch.object(tasks.send_notification_email, "delay")
    def test_course_completion_notification(self, mock_delay):
        CourseProgress.objects.create(
            user=self.student, course=self.course, percent=100
        )

        notif = Notification.objects.filter(
            recipient=self.student,
            verb__contains="Congratulations"
        ).first()
        self.assertIsNotNone(notif)
        mock_delay.assert_called_once()

    @patch.object(tasks.send_notification_email, "delay")
    def test_new_lesson_published_notification(self, mock_delay):
        # 1) enroll the student (fires enrollment signal)
        Enrollment.objects.create(user=self.student, course=self.course)
        # clear that call so we only assert on the new-lesson signal below
        mock_delay.reset_mock()

        # 2) publish a new lesson
        new_lesson = Lesson.objects.create(
            course=self.course, title="Brand New", content="", order=3
        )

        # in-app notification exists
        notif = Notification.objects.filter(
            recipient=self.student,
            verb__contains="New lesson available"
        ).first()
        self.assertIsNotNone(notif)

        # exactly one email task for the new-lesson notification
        mock_delay.assert_called_once_with(
            self.student.email,
            f"New lesson in {self.course.title}",
            f"Hi {self.student.username}, a new lesson “{new_lesson.title}” has just been published."
        )
