from django.test import TestCase
from django.contrib.auth import get_user_model

from courses.models import Course, Lesson
from scorm_player.models import ScormPackage
from progress.models import (
    LessonProgress,
    ScormPackageProgress,
    Certification,
    ScormCertification,
)

User = get_user_model()

class CertificationSignalsTests(TestCase):
    def setUp(self):
        # create a user
        self.user = User.objects.create_user(
            username="tester", email="test@example.com", password="pass"
        )

        # create a course and lesson
        self.course = Course.objects.create(
            title="Course A", description="Desc", price=0, instructor=self.user
        )
        self.lesson = Lesson.objects.create(
            course=self.course, title="Lesson 1", content="...", order=1
        )

        # create a SCORM package
        self.pkg = ScormPackage.objects.create(
            title="Package A", course=self.course, file="fake.zip", version="1.2", uploaded_by=self.user
        )

    def test_lesson_progress_triggers_certification(self):
        # no cert initially
        self.assertFalse(
            Certification.objects.filter(user=self.user, lesson=self.lesson).exists()
        )

        # mark lesson complete → signal should award Certification
        LessonProgress.objects.create(
            user=self.user,
            lesson=self.lesson,
            is_completed=True
        )

        cert = Certification.objects.get(user=self.user, lesson=self.lesson)
        self.assertIsNotNone(cert.issued_at)
        self.assertTrue(cert.cert_id)  # uuid generated

    def test_lesson_progress_not_completed_no_certification(self):
        # create a progress record without completing → no Certification
        LessonProgress.objects.create(
            user=self.user,
            lesson=self.lesson,
            is_completed=False
        )
        self.assertFalse(
            Certification.objects.filter(user=self.user, lesson=self.lesson).exists()
        )

    def test_scorm_progress_triggers_scorm_certification_on_create(self):
        # no scorm cert initially
        self.assertFalse(
            ScormCertification.objects.filter(user=self.user, package=self.pkg).exists()
        )

        # create SCORM progress at 100% → signal should award ScormCertification
        ScormPackageProgress.objects.create(
            user=self.user,
            package=self.pkg,
            percent=100.0
        )

        scert = ScormCertification.objects.get(user=self.user, package=self.pkg)
        self.assertIsNotNone(scert.issued_at)
        self.assertTrue(scert.cert_id)

    def test_scorm_progress_no_certification_below_100(self):
        # create SCORM progress below threshold → no ScormCertification
        ScormPackageProgress.objects.create(
            user=self.user,
            package=self.pkg,
            percent=50.0
        )
        self.assertFalse(
            ScormCertification.objects.filter(user=self.user, package=self.pkg).exists()
        )

    def test_scorm_progress_triggers_scorm_certification_on_update(self):
        # initial progress below 100%
        prog = ScormPackageProgress.objects.create(
            user=self.user,
            package=self.pkg,
            percent=50.0
        )
        self.assertFalse(
            ScormCertification.objects.filter(user=self.user, package=self.pkg).exists()
        )

        # update to 100% → signal should award ScormCertification
        prog.percent = 100.0
        prog.save()

        scert = ScormCertification.objects.get(user=self.user, package=self.pkg)
        self.assertIsNotNone(scert.issued_at)
        self.assertTrue(scert.cert_id)
