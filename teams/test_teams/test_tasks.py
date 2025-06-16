from django.test import TestCase
from django.contrib.auth import get_user_model
from teams.tasks import snapshot_team_analytics
from teams.models import Organization, TeamAnalyticsSnapshot, TeamMember, BulkPurchase
from courses.models import Course, Module, Lesson
from progress.models import LessonProgress
from django.db.models.signals import post_save

from progress.signals import update_course_progress
from notifications.signals import lesson_progress_notification


User = get_user_model()

class TasksTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Disconnect only for this test class
        post_save.disconnect(update_course_progress, sender=LessonProgress)
        post_save.disconnect(lesson_progress_notification, sender=LessonProgress)

    @classmethod
    def tearDownClass(cls):
        # Re-connect so other tests aren’t affected
        post_save.connect(update_course_progress, sender=LessonProgress)
        post_save.connect(lesson_progress_notification, sender=LessonProgress)
        super().tearDownClass()

    def setUp(self):
        # Create users
        self.admin = User.objects.create_user(
            username="admin",
            email="admin@test.com",
            password="pass"
        )
        self.member = User.objects.create_user(
            username="member",
            email="member@test.com",
            password="pass"
        )

        # Create organization and bulk purchase
        self.org = Organization.objects.create(name="Org", admin=self.admin)
        self.bp = BulkPurchase.objects.create(
            organization=self.org,
            purchased_by=self.admin,
            seats=3,
            order_reference="REF"
        )
        # Link a course to the bulk purchase
        self.course = Course.objects.create(
            title="C", description="D", price=0, instructor=self.admin
        )
        self.bp.courses.add(self.course)

        # Add an active team member
        self.tm_active = TeamMember.objects.create(
            organization=self.org,
            user=self.member,
            invited_by=self.admin,
            status=TeamMember.ACTIVE
        )

        # Create module and lessons for progress tracking
        self.module = Module.objects.create(
            course=self.course,
            title="Module 1",
            description="",
            order=1
        )
        self.lesson1 = Lesson.objects.create(
            module=self.module,
            title="Lesson 1",
            content="",
            order=1
        )
        self.lesson2 = Lesson.objects.create(
            module=self.module,
            title="Lesson 2",
            content="",
            order=2
        )

        # Record lesson progress: one complete, one incomplete
        LessonProgress.objects.create(user=self.member, lesson=self.lesson1, is_completed=True)
        LessonProgress.objects.create(user=self.member, lesson=self.lesson2, is_completed=False)

    def test_snapshot_creation(self):
        # No snapshots initially
        self.assertFalse(TeamAnalyticsSnapshot.objects.exists())
        # Run the task
        snapshot_team_analytics()
        # Snapshot should now exist for our organization
        snaps = TeamAnalyticsSnapshot.objects.filter(organization=self.org)
        self.assertEqual(snaps.count(), 1)

    def test_snapshot_data_accuracy(self):
        # Run the task
        snapshot_team_analytics()
        snap = TeamAnalyticsSnapshot.objects.get(organization=self.org)

        # Verify seat usage in snapshot
        expected_seat_usage = {"total_seats": 3, "used_seats": 1, "pending_invites": 0}
        self.assertEqual(snap.seat_usage, expected_seat_usage)

        # Verify learning progress list
        progress_list = snap.learning_progress
        self.assertEqual(len(progress_list), 1)
        record = progress_list[0]
        self.assertEqual(record["user_id"], self.member.id)
        self.assertEqual(record["email"], self.member.email)
        self.assertEqual(record["completed"], 1)
        self.assertEqual(record["total"], 2)
        self.assertEqual(record["percent"], 50)