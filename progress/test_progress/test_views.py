from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

from courses.models import Course, Lesson
from scorm_player.models import ScormPackage
from progress.models import (
    LessonProgress,
    CourseProgress,
    ScormPackageProgress,
    
)

User = get_user_model()

class ProgressViewsTests(APITestCase):
    def setUp(self):
        # user + auth
        self.user = User.objects.create_user("bob", "bob@example.com", "pass")
        self.client.force_authenticate(self.user)

        # course, lesson, scorm package
        self.course = Course.objects.create(
            title="C2", description="desc", price=0, instructor=self.user
        )
        self.lesson = Lesson.objects.create(
            course=self.course, title="L2", content="...", order=1
        )
        self.pkg = ScormPackage.objects.create(
            title="P2",
            course=self.course,
            file="fake2.zip",
            version="1.2",
            uploaded_by=self.user,
        )

    def test_create_and_list_lesson_progress(self):
        url = reverse("progress:lesson-progress-list")
        resp = self.client.post(url, {"lesson": self.lesson.id})
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data["lesson"], self.lesson.id)

        # list
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 1)

    def test_mark_lesson_complete(self):
        lp = LessonProgress.objects.create(user=self.user, lesson=self.lesson)
        url = reverse("progress:lesson-progress-complete", args=[lp.id])
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        lp.refresh_from_db()
        self.assertTrue(lp.is_completed)

    def test_course_progress_readonly(self):
        url = reverse("progress:course-progress-list")
        resp = self.client.get(url)
        self.assertEqual(resp.data, [])

        cp = CourseProgress.objects.create(user=self.user, course=self.course, percent=42)
        resp = self.client.get(url)
        self.assertEqual(len(resp.data), 1)
        self.assertEqual(float(resp.data[0]["percent"]), 42)

    def test_scorm_progress_readonly(self):
        url = reverse("progress:scorm-progress-list")
        resp = self.client.get(url)
        self.assertEqual(resp.data, [])

        sp = ScormPackageProgress.objects.create(user=self.user, package=self.pkg, percent=88)
        resp = self.client.get(url)
        self.assertEqual(len(resp.data), 1)
        self.assertEqual(float(resp.data[0]["percent"]), 88)

    def test_lesson_certification_endpoint(self):
        certs_url = reverse("progress:certification-list")
        # no certs yet
        resp = self.client.get(certs_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, [])

        # create a completed LessonProgress → signal should award cert
        LessonProgress.objects.create(
            user=self.user,
            lesson=self.lesson,
            is_completed=True
        )

        resp = self.client.get(certs_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 1)
        cert = resp.data[0]
        self.assertEqual(cert["lesson"], self.lesson.id)
        self.assertIn("cert_id", cert)
        self.assertIn("issued_at", cert)

    def test_scorm_certification_endpoint(self):
        scert_url = reverse("progress:scorm-certification-list")
        # no SCORM certs yet
        resp = self.client.get(scert_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, [])

        # create a SCORM progress <100% → no cert
        scpp = ScormPackageProgress.objects.create(
            user=self.user,
            package=self.pkg,
            percent=50.0
        )
        resp = self.client.get(scert_url)
        self.assertEqual(resp.data, [])

        # update to 100% → signal should award SCORM cert
        scpp.percent = 100.0
        scpp.save()

        resp = self.client.get(scert_url)
        self.assertEqual(len(resp.data), 1)
        scert = resp.data[0]
        self.assertEqual(scert["package"], self.pkg.id)
        self.assertIn("cert_id", scert)
        self.assertIn("issued_at", scert)
