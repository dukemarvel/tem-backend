from django.test import TestCase
from django.contrib.auth import get_user_model
from courses.models import Course, Lesson
from scorm_player.models import ScormPackage
from progress.models import (
    LessonProgress,
    CourseProgress,
    ScormPackageProgress,
    Certification,
    ScormCertification,
)
import uuid

User = get_user_model()

class ProgressModelTests(TestCase):
    def setUp(self):
        # users
        self.user = User.objects.create_user("alice", "alice@example.com", "pass")
        # course & lessons
        self.course = Course.objects.create(
            title="C1", description="desc", price=0, instructor=self.user
        )
        self.lesson1 = Lesson.objects.create(
            course=self.course, title="L1", content="...", order=1
        )
        # SCORM package (now requires a course)
        self.pkg = ScormPackage.objects.create(
            title="P1",
            course=self.course,
            file="fake.zip",
            version="1.2",
            uploaded_by=self.user,
        )

    def test_lesson_progress_defaults_and_uniqueness(self):
        lp = LessonProgress.objects.create(user=self.user, lesson=self.lesson1)
        self.assertFalse(lp.is_completed)
        with self.assertRaises(Exception):
            LessonProgress.objects.create(user=self.user, lesson=self.lesson1)

    def test_course_progress_defaults_and_uniqueness(self):
        cp = CourseProgress.objects.create(user=self.user, course=self.course)
        self.assertEqual(cp.percent, 0)
        with self.assertRaises(Exception):
            CourseProgress.objects.create(user=self.user, course=self.course)

    def test_scorm_package_progress_defaults_and_uniqueness(self):
        sp = ScormPackageProgress.objects.create(user=self.user, package=self.pkg)
        self.assertEqual(sp.percent, 0)
        with self.assertRaises(Exception):
            ScormPackageProgress.objects.create(user=self.user, package=self.pkg)

    def test_certification_defaults_and_uniqueness(self):
        cert = Certification.objects.create(user=self.user, lesson=self.lesson1)
        self.assertIsInstance(cert.cert_id, uuid.UUID)
        with self.assertRaises(Exception):
            Certification.objects.create(user=self.user, lesson=self.lesson1)
        self.assertIn(self.lesson1.title, str(cert))

    def test_scorm_certification_defaults_and_uniqueness(self):
        scert = ScormCertification.objects.create(user=self.user, package=self.pkg)
        self.assertIsInstance(scert.cert_id, uuid.UUID)
        with self.assertRaises(Exception):
            ScormCertification.objects.create(user=self.user, package=self.pkg)
        self.assertIn(self.pkg.title, str(scert))
