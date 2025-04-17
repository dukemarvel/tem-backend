# courses/tests/test_views.py

from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from auth_app.models import InstructorProfile, StudentProfile
from courses.models import Course, Lesson

User = get_user_model()


class CourseViewSetTest(APITestCase):
    def setUp(self):
        # instructor user
        self.instructor = User.objects.create_user(
            email="inst@x.com", username="inst", password="pass"
        )
        InstructorProfile.objects.create(user=self.instructor)

        # student user
        self.student = User.objects.create_user(
            email="stud@x.com", username="stud", password="pass"
        )
        StudentProfile.objects.create(user=self.student)

        self.course = Course.objects.create(
            title="Existing",
            description="Desc",
            price=20.00,
            instructor=self.instructor
        )
        self.list_url = reverse("courses:courses-list")
        self.detail_url = lambda pk: reverse("courses:courses-detail", args=[pk])

    def test_list_unauthenticated(self):
        r = self.client.get(self.list_url)
        self.assertEqual(r.status_code, 401)

    def test_list_authenticated(self):
        self.client.force_authenticate(self.student)
        r = self.client.get(self.list_url)
        self.assertEqual(r.status_code, 200)
        titles = [c["title"] for c in r.data]
        self.assertIn("Existing", titles)

    def test_retrieve(self):
        self.client.force_authenticate(self.student)
        r = self.client.get(self.detail_url(self.course.id))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["title"], "Existing")

    def test_create_by_instructor(self):
        self.client.force_authenticate(self.instructor)
        payload = {"title":"New Course","description":"D","price":15.0}
        r = self.client.post(self.list_url, payload)
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.data["instructor"], self.instructor.id)

    def test_create_by_student_forbidden(self):
        self.client.force_authenticate(self.student)
        payload = {"title":"New","description":"D","price":5.0}
        r = self.client.post(self.list_url, payload)
        self.assertEqual(r.status_code, 403)

    def test_update_by_instructor(self):
        self.client.force_authenticate(self.instructor)
        r = self.client.patch(self.detail_url(self.course.id), {"title":"Upd"})
        self.assertEqual(r.status_code, 200)
        self.course.refresh_from_db()
        self.assertEqual(self.course.title, "Upd")

    def test_update_by_student_forbidden(self):
        self.client.force_authenticate(self.student)
        r = self.client.patch(self.detail_url(self.course.id), {"title":"X"})
        self.assertEqual(r.status_code, 403)

    def test_delete_by_instructor(self):
        self.client.force_authenticate(self.instructor)
        r = self.client.delete(self.detail_url(self.course.id))
        self.assertEqual(r.status_code, 204)
        self.assertFalse(Course.objects.filter(id=self.course.id).exists())

    def test_delete_by_student_forbidden(self):
        self.client.force_authenticate(self.student)
        r = self.client.delete(self.detail_url(self.course.id))
        self.assertEqual(r.status_code, 403)


class LessonViewSetTest(APITestCase):
    def setUp(self):
        # instructor + course
        self.instructor = User.objects.create_user(
            email="i2@x.com", username="i2", password="pass"
        )
        InstructorProfile.objects.create(user=self.instructor)
        self.course = Course.objects.create(
            title="C",
            description="D",
            price=0,
            instructor=self.instructor,
        )

        # student
        self.student = User.objects.create_user(
            email="s2@x.com", username="s2", password="pass"
        )
        StudentProfile.objects.create(user=self.student)

        self.lesson = Lesson.objects.create(
            course=self.course,
            title="Lsn",
            content="Cnt",
            order=2
        )
        self.list_url = reverse("courses:lessons-list")
        self.detail_url = lambda pk: reverse("courses:lessons-detail", args=[pk])

    def test_list_unauthenticated(self):
        r = self.client.get(self.list_url)
        self.assertEqual(r.status_code, 401)

    def test_list_authenticated(self):
        self.client.force_authenticate(self.student)
        r = self.client.get(self.list_url)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.data), 1)

    def test_retrieve(self):
        self.client.force_authenticate(self.student)
        r = self.client.get(self.detail_url(self.lesson.id))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["title"], "Lsn")

    def test_create_by_instructor(self):
        self.client.force_authenticate(self.instructor)
        payload = {
            "title": "NewL",
            "content": "C",
            "order": 3,
            "course_id": self.course.id
        }
        r = self.client.post(self.list_url, payload)
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.data["title"], "NewL")

    def test_create_without_course_id(self):
        self.client.force_authenticate(self.instructor)
        r = self.client.post(self.list_url, {"title":"X","content":"Y"})
        self.assertEqual(r.status_code, 400)

    def test_create_by_student_forbidden(self):
        self.client.force_authenticate(self.student)
        payload = {
            "title": "X","content":"Y","order":1,
            "course_id": self.course.id
        }
        r = self.client.post(self.list_url, payload)
        self.assertEqual(r.status_code, 403)

    def test_update_by_instructor(self):
        self.client.force_authenticate(self.instructor)
        r = self.client.patch(self.detail_url(self.lesson.id), {"title":"Up"})
        self.assertEqual(r.status_code, 200)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.title, "Up")

    def test_update_by_student_forbidden(self):
        self.client.force_authenticate(self.student)
        r = self.client.patch(self.detail_url(self.lesson.id), {"title":"Bad"})
        self.assertEqual(r.status_code, 403)

    def test_delete_by_instructor(self):
        self.client.force_authenticate(self.instructor)
        r = self.client.delete(self.detail_url(self.lesson.id))
        self.assertEqual(r.status_code, 204)
        self.assertFalse(Lesson.objects.filter(id=self.lesson.id).exists())

    def test_delete_by_student_forbidden(self):
        self.client.force_authenticate(self.student)
        r = self.client.delete(self.detail_url(self.lesson.id))
        self.assertEqual(r.status_code, 403)
