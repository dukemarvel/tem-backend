from django.test import TestCase
from django.contrib.auth import get_user_model
from auth_app.models import InstructorProfile
from courses.models import Course, Lesson, Quiz, Question, Choice

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
        self.assertEqual(str(self.course), "Test Course (by inst@example.com)")

    def test_created_at_auto_now_add(self):
        self.assertIsNotNone(self.course.created_at)


class LessonModelTest(TestCase):
    def setUp(self):
        user = User.objects.create_user(
            email="inst2@example.com", username="inst2", password="pass"
        )
        InstructorProfile.objects.create(user=user)
        course = Course.objects.create(
            title="C2", description="Desc2", price=10.00, instructor=user
        )
        self.lesson = Lesson.objects.create(
            course=course,
            title="L1",
            content="Lesson content",
            video_url="http://example.com",
            order=1,
        )

    def test_str_returns_lesson_and_course(self):
        self.assertEqual(str(self.lesson), "Lesson: L1 in C2")

    def test_defaults_for_optional_fields(self):
        l2 = Lesson.objects.create(
            course=self.lesson.course,
            title="L2",
            content="More content"
        )
        # default order, and no video or external URL
        self.assertEqual(l2.order, 0)
        self.assertFalse(l2.video)            # FileField is empty
        self.assertIsNone(l2.video_url)

    def test_created_at_auto_now_add(self):
        self.assertIsNotNone(self.lesson.created_at)


class QuizQuestionChoiceModelTest(TestCase):
    def setUp(self):
        user = User.objects.create_user(
            email="qinst@example.com", username="qinst", password="pass"
        )
        InstructorProfile.objects.create(user=user)
        course = Course.objects.create(
            title="QC", description="QD", price=0, instructor=user
        )
        lesson = Lesson.objects.create(course=course, title="LQ", content="CQ")
        self.quiz = Quiz.objects.create(lesson=lesson, title="Sample Quiz")
        self.q1 = Question.objects.create(quiz=self.quiz, text="Q1", order=2)
        # default order for Q2 is 0
        self.q2 = Question.objects.create(quiz=self.quiz, text="Q2")
        self.c1 = Choice.objects.create(question=self.q1, text="A1", is_correct=True)
        self.c2 = Choice.objects.create(question=self.q1, text="A2", is_correct=False)

    def test_quiz_question_choice_relationships(self):
        self.assertEqual(self.quiz.lesson, self.q1.quiz.lesson)
        self.assertIn(self.q1, list(self.quiz.questions.all()))
        self.assertIn(self.q2, list(self.quiz.questions.all()))
        self.assertEqual(self.q2.order, 0)

        # choices on q1
        choices = list(self.q1.choices.all())
        self.assertIn(self.c1, choices)
        self.assertIn(self.c2, choices)
        self.assertTrue(self.c1.is_correct)
        self.assertFalse(self.c2.is_correct)
