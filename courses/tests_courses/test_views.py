from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from auth_app.models import InstructorProfile, StudentProfile
from courses.models import Course, Lesson, Quiz, Question, Choice

User = get_user_model()

class CourseViewSetTest(APITestCase):
    def setUp(self):
        inst = User.objects.create_user(
            email="inst@x.com", username="inst", password="pass"
        )
        InstructorProfile.objects.create(user=inst)
        stud = User.objects.create_user(
            email="stud@x.com", username="stud", password="pass"
        )
        StudentProfile.objects.create(user=stud)

        self.instructor = inst
        self.student = stud
        self.course = Course.objects.create(
            title="Existing", description="Desc", price=20.00, instructor=inst
        )
        self.list_url = reverse("courses:courses-list")
        self.detail_url = lambda pk: reverse("courses:courses-detail", args=[pk])

    def test_list_requires_auth(self):
        res = self.client.get(self.list_url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_authenticated(self):
        self.client.force_authenticate(self.student)
        res = self.client.get(self.list_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        titles = [c["title"] for c in res.data]
        self.assertIn("Existing", titles)

    def test_retrieve(self):
        self.client.force_authenticate(self.student)
        res = self.client.get(self.detail_url(self.course.id))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["title"], "Existing")

    def test_create_by_instructor(self):
        self.client.force_authenticate(self.instructor)
        payload = {"title": "New Course", "description": "D", "price": 15.0}
        res = self.client.post(self.list_url, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["instructor"], self.instructor.id)

    def test_create_by_student_forbidden(self):
        self.client.force_authenticate(self.student)
        payload = {"title": "X", "description": "D", "price": 5.0}
        res = self.client.post(self.list_url, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_by_instructor(self):
        self.client.force_authenticate(self.instructor)
        res = self.client.patch(self.detail_url(self.course.id), {"title": "Upd"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.course.refresh_from_db()
        self.assertEqual(self.course.title, "Upd")

    def test_delete_by_instructor(self):
        self.client.force_authenticate(self.instructor)
        res = self.client.delete(self.detail_url(self.course.id))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Course.objects.filter(pk=self.course.id).exists())


class LessonViewSetTest(APITestCase):
    def setUp(self):
        inst = User.objects.create_user(
            email="i2@x.com", username="i2", password="pass"
        )
        InstructorProfile.objects.create(user=inst)
        self.instructor = inst

        course = Course.objects.create(
            title="C", description="D", price=0, instructor=inst
        )
        self.course = course

        stud = User.objects.create_user(
            email="s2@x.com", username="s2", password="pass"
        )
        StudentProfile.objects.create(user=stud)
        self.student = stud

        self.lesson = Lesson.objects.create(
            course=course, title="Lsn", content="Cnt", order=2
        )
        self.list_url = reverse("courses:lessons-list")
        self.detail_url = lambda pk: reverse("courses:lessons-detail", args=[pk])
        self.upload_url = lambda pk: reverse("courses:lessons-upload_video", args=[pk])

    def test_list_requires_auth(self):
        res = self.client.get(self.list_url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_authenticated(self):
        self.client.force_authenticate(self.student)
        res = self.client.get(self.list_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

    def test_retrieve(self):
        self.client.force_authenticate(self.student)
        res = self.client.get(self.detail_url(self.lesson.id))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["title"], "Lsn")

    def test_create_by_instructor(self):
        self.client.force_authenticate(self.instructor)
        payload = {
            "title": "NewL",
            "content": "C",
            "order": 3,
            "course": self.course.id,           
        }
        res = self.client.post(self.list_url, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["title"], "NewL")

    def test_create_without_course(self):
        self.client.force_authenticate(self.instructor)
        res = self.client.post(self.list_url, {"title": "X", "content": "Y"})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_by_student_forbidden(self):
        self.client.force_authenticate(self.student)
        payload = {
            "title": "X", "content": "Y", "order": 1,
            "course": self.course.id,
        }
        res = self.client.post(self.list_url, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_upload_video_missing_file(self):
        self.client.force_authenticate(self.instructor)
        res = self.client.post(self.upload_url(self.lesson.id), {})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_upload_video_success(self):
        self.client.force_authenticate(self.instructor)
        dummy = SimpleUploadedFile("vid.mp4", b"12345", content_type="video/mp4")
        res = self.client.post(self.upload_url(self.lesson.id), {"video": dummy})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.lesson.refresh_from_db()
        self.assertTrue(self.lesson.video.name.endswith("vid.mp4"))

    def test_upload_video_forbidden_to_student(self):
        self.client.force_authenticate(self.student)
        dummy = SimpleUploadedFile("v.mp4", b"x", content_type="video/mp4")
        res = self.client.post(self.upload_url(self.lesson.id), {"video": dummy})
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class QuizViewSetTest(APITestCase):
    def setUp(self):
        inst = User.objects.create_user(
            email="qi@x.com", username="qi", password="pass"
        )
        InstructorProfile.objects.create(user=inst)
        stud = User.objects.create_user(
            email="qs@x.com", username="qs", password="pass"
        )
        StudentProfile.objects.create(user=stud)

        course = Course.objects.create(
            title="QC", description="QD", price=0, instructor=inst
        )
        lesson = Lesson.objects.create(course=course, title="LQ", content="CQ")
        self.instructor = inst
        self.student = stud
        self.lesson = lesson

        # existing quiz
        self.quiz = Quiz.objects.create(lesson=lesson, title="Old Quiz")
        q = Question.objects.create(quiz=self.quiz, text="OldQ", order=1)
        Choice.objects.create(question=q, text="OldA1", is_correct=True)

        self.list_url = reverse("courses:quizzes-list")
        self.detail_url = lambda pk: reverse("courses:quizzes-detail", args=[pk])

    def _make_payload(self):
        return {
            "lesson": self.lesson.id,
            "title": "New Quiz",
            "questions": [
                {
                    "text": "Q1", "order": 1,
                    "choices": [
                        {"text": "A1", "is_correct": True},
                        {"text": "A2", "is_correct": False},
                    ]
                }
            ]
        }

    def test_create_by_instructor(self):
        self.client.force_authenticate(self.instructor)
        res = self.client.post(self.list_url, self._make_payload(), format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Quiz.objects.count(), 2)

    def test_create_by_student_forbidden(self):
        self.client.force_authenticate(self.student)
        res = self.client.post(self.list_url, self._make_payload(), format="json")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_contains_questions(self):
        self.client.force_authenticate(self.student)
        res = self.client.get(self.detail_url(self.quiz.id))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIsInstance(res.data["questions"], list)

    def test_update_by_instructor(self):
        self.client.force_authenticate(self.instructor)
        payload = self._make_payload()
        payload["title"] = "Updated"
        res = self.client.put(self.detail_url(self.quiz.id), payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(Quiz.objects.get(pk=self.quiz.id).title, "Updated")

    def test_delete_by_student_forbidden(self):
        self.client.force_authenticate(self.student)
        res = self.client.delete(self.detail_url(self.quiz.id))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class QuizSubmissionTest(APITestCase):
    def setUp(self):
        inst = User.objects.create_user(
            email="sub@x.com", username="subi", password="pass"
        )
        InstructorProfile.objects.create(user=inst)
        stud = User.objects.create_user(
            email="subs@x.com", username="subs", password="pass"
        )
        StudentProfile.objects.create(user=stud)

        course = Course.objects.create(
            title="CS", description="DS", price=0, instructor=inst
        )
        lesson = Lesson.objects.create(course=course, title="LS", content="CS")
        quiz = Quiz.objects.create(lesson=lesson, title="SQuiz")
        q1 = Question.objects.create(quiz=quiz, text="Q1", order=1)
        q2 = Question.objects.create(quiz=quiz, text="Q2", order=2)
        c1 = Choice.objects.create(question=q1, text="A1", is_correct=True)
        Choice.objects.create(question=q2, text="B1", is_correct=False)

        self.quiz = quiz
        self.student = stud
        self.submit_url = reverse("courses:quizzesubmit-submit", args=[quiz.id])
        self.answers = { str(q1.id): c1.id, str(q2.id): 0 }

    def test_submit_scores(self):
        self.client.force_authenticate(self.student)
        res = self.client.post(self.submit_url, {"answers": self.answers}, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["correct"], 1)
        self.assertEqual(res.data["total"], 2)

    def test_submit_unauthenticated(self):
        res = self.client.post(self.submit_url, {"answers": {}}, format="json")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_submit_nonexistent_quiz(self):
        self.client.force_authenticate(self.student)
        bad = reverse("courses:quizzesubmit-submit", args=[99999])
        res = self.client.post(bad, {"answers": {}}, format="json")
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
