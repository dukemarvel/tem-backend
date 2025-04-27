from django.test import TestCase
from django.contrib.auth import get_user_model

from courses.models import Course, Lesson
from scorm_player.models import ScormPackage, Sco, RuntimeData
from progress.models import CourseProgress, ScormPackageProgress, LessonProgress
from progress.tasks import recalc_course_progress, recalc_scorm_progress

User = get_user_model()

class TasksTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="bob", email="bob@example.com", password="pass"
        )
        # Course + lessons
        self.course = Course.objects.create(
            title="My Course", description="d", price=0, instructor=self.user
        )
        self.lesson1 = Lesson.objects.create(course=self.course, title="L1", content="", order=1)
        self.lesson2 = Lesson.objects.create(course=self.course, title="L2", content="", order=2)

        # SCORM package + 3 SCOs
        self.pkg = ScormPackage.objects.create(
            title="Pack", file="f.zip", version="1.2", uploaded_by=self.user
        )
        self.sco1 = Sco.objects.create(package=self.pkg, identifier="i1", launch_url="u1", title="S1", sequence=0)
        self.sco2 = Sco.objects.create(package=self.pkg, identifier="i2", launch_url="u2", title="S2", sequence=1)
        self.sco3 = Sco.objects.create(package=self.pkg, identifier="i3", launch_url="u3", title="S3", sequence=2)

    def test_recalc_course_progress_no_lessons(self):
        # new course2 with zero lessons
        course2 = Course.objects.create(
            title="Empty", description="d", price=0, instructor=self.user
        )
        recalc_course_progress.run(self.user.id, course2.id)
        cp = CourseProgress.objects.get(user=self.user, course=course2)
        self.assertEqual(float(cp.percent), 0.00)

    def test_recalc_course_progress_partial_and_full(self):
        # 1 of 2 lessons complete
        LessonProgress.objects.create(user=self.user, lesson=self.lesson1, is_completed=True)
        recalc_course_progress.run(self.user.id, self.course.id)
        cp = CourseProgress.objects.get(user=self.user, course=self.course)
        self.assertAlmostEqual(float(cp.percent), 50.00)

        # 2 of 2 lessons complete
        LessonProgress.objects.create(user=self.user, lesson=self.lesson2, is_completed=True)
        recalc_course_progress.run(self.user.id, self.course.id)
        cp.refresh_from_db()
        self.assertEqual(float(cp.percent), 100.00)

    def test_recalc_scorm_progress_no_scos(self):
        # package2 has no SCOs
        pkg2 = ScormPackage.objects.create(
            title="NoSCO", file="g.zip", version="1.2", uploaded_by=self.user
        )
        recalc_scorm_progress.run(self.user.id, pkg2.id)
        sp = ScormPackageProgress.objects.get(user=self.user, package=pkg2)
        self.assertEqual(float(sp.percent), 0.00)

    def test_recalc_scorm_progress_various_statuses(self):
        # initial: no runtimedata → 0%
        recalc_scorm_progress.run(self.user.id, self.pkg.id)
        sp = ScormPackageProgress.objects.get(user=self.user, package=self.pkg)
        self.assertEqual(float(sp.percent), 0.00)

        # create two complete/pass statuses and one incomplete
        RuntimeData.objects.create(user=self.user, sco=self.sco1, data={"cmi.core.lesson_status": "completed"})
        RuntimeData.objects.create(user=self.user, sco=self.sco2, data={"cmi.success_status": "passed"})
        RuntimeData.objects.create(user=self.user, sco=self.sco3, data={"foo": "bar"})
        recalc_scorm_progress.run(self.user.id, self.pkg.id)
        sp.refresh_from_db()
        # 2 of 3 → ~66.67%
        self.assertAlmostEqual(float(sp.percent), 66.67, places=2)