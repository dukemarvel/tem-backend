from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model

from courses.models import Course, Lesson
from scorm_player.models import ScormPackage, Sco, RuntimeData
from progress.models import LessonProgress, CourseProgress, ScormPackageProgress

User = get_user_model()

@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class SignalsTests(TestCase):
    def setUp(self):
        # common fixtures
        self.user = User.objects.create_user(
            username="alice", email="alice@example.com", password="pass"
        )

        # Course with two lessons
        self.course = Course.objects.create(
            title="Test Course", description="desc", price=0, instructor=self.user
        )
        self.lesson1 = Lesson.objects.create(
            course=self.course, title="L1", content="...", order=1
        )
        self.lesson2 = Lesson.objects.create(
            course=self.course, title="L2", content="...", order=2
        )

        # SCORM package with two SCOs
        self.pkg = ScormPackage.objects.create(
            title="SCORM Pack", file="fake.zip", version="1.2", uploaded_by=self.user
        )
        self.sco1 = Sco.objects.create(
            package=self.pkg, identifier="id1", launch_url="u1", title="S1", sequence=0
        )
        self.sco2 = Sco.objects.create(
            package=self.pkg, identifier="id2", launch_url="u2", title="S2", sequence=1
        )

    def test_lesson_progress_signal_triggers_course_progress(self):
        # no CourseProgress yet
        self.assertFalse(
            CourseProgress.objects.filter(user=self.user, course=self.course).exists()
        )

        # mark first lesson complete → percent should be 50%
        LessonProgress.objects.create(user=self.user, lesson=self.lesson1, is_completed=True)
        cp = CourseProgress.objects.get(user=self.user, course=self.course)
        self.assertEqual(float(cp.percent), 50.00)

        # mark second lesson complete → percent should jump to 100%
        LessonProgress.objects.create(user=self.user, lesson=self.lesson2, is_completed=True)
        cp.refresh_from_db()
        self.assertEqual(float(cp.percent), 100.00)

    def test_runtimedata_signal_triggers_scorm_progress(self):
        # no ScormPackageProgress yet
        self.assertFalse(
            ScormPackageProgress.objects.filter(user=self.user, package=self.pkg).exists()
        )

        # first runtimedata → 1 of 2 SCOs completed
        RuntimeData.objects.create(
            user=self.user,
            sco=self.sco1,
            data={"cmi.core.lesson_status": "completed"}
        )
        sp = ScormPackageProgress.objects.get(user=self.user, package=self.pkg)
        self.assertEqual(float(sp.percent), 50.00)

        # second runtimedata → now 2 of 2 SCOs
        RuntimeData.objects.create(
            user=self.user,
            sco=self.sco2,
            data={"cmi.success_status": "passed"}
        )
        sp.refresh_from_db()
        self.assertEqual(float(sp.percent), 100.00)
