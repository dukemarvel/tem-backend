from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from datetime import date, timedelta
from auth_app.models import InstructorProfile, StudentProfile
from courses.models import (
    Course, Module, Lesson, Quiz, Question, Choice,
    Tag, Review, WishlistItem, Promotion
)

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

    def test_average_rating_default_zero(self):
        self.assertEqual(self.course.average_rating, 0)


class ModuleModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="modinst@example.com", username="modinst", password="pass"
        )
        InstructorProfile.objects.create(user=self.user)
        self.course = Course.objects.create(
            title="C-Mod", description="Module course", price=0, instructor=self.user
        )
        self.module = Module.objects.create(
            course=self.course, title="M1", description="First module", order=1
        )

    def test_str_returns_title_and_course(self):
        expected = f"{self.module.title} — {self.course.title}"
        self.assertEqual(str(self.module), expected)

    def test_default_order(self):
        m2 = Module.objects.create(course=self.course, title="M2")
        self.assertEqual(m2.order, 0)


class LessonModelTest(TestCase):
    def setUp(self):
        user = User.objects.create_user(
            email="inst2@example.com", username="inst2", password="pass"
        )
        InstructorProfile.objects.create(user=user)
        course = Course.objects.create(
            title="C2", description="Desc2", price=10.00, instructor=user
        )
        self.module = Module.objects.create(course=course, title="Mod-A")
        self.lesson = Lesson.objects.create(
            module=self.module,
            title="L1",
            content="Lesson content",
            video_url="http://example.com",
            order=1,
        )

    def test_str_returns_lesson_and_module(self):
        expected = f"Lesson: {self.lesson.title} in {self.module.title}"
        self.assertEqual(str(self.lesson), expected)

    def test_defaults_for_optional_fields(self):
        l2 = Lesson.objects.create(
            module=self.module,
            title="L2",
            content="More content"
        )
        self.assertEqual(l2.order, 0)
        self.assertFalse(l2.video)
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
        module = Module.objects.create(course=course, title="Mod-QC")
        lesson = Lesson.objects.create(module=module, title="LQ", content="CQ")
        self.quiz = Quiz.objects.create(lesson=lesson, title="Sample Quiz")
        self.q1 = Question.objects.create(quiz=self.quiz, text="Q1", order=2)
        self.q2 = Question.objects.create(quiz=self.quiz, text="Q2")
        self.c1 = Choice.objects.create(question=self.q1, text="A1", is_correct=True)
        self.c2 = Choice.objects.create(question=self.q1, text="A2", is_correct=False)

    def test_relationships_and_defaults(self):
        self.assertEqual(self.quiz.lesson, self.q1.quiz.lesson)
        self.assertIn(self.q1, self.quiz.questions.all())
        self.assertIn(self.q2, self.quiz.questions.all())
        self.assertEqual(self.q2.order, 0)
        self.assertIn(self.c1, self.q1.choices.all())
        self.assertIn(self.c2, self.q1.choices.all())
        self.assertTrue(self.c1.is_correct)
        self.assertFalse(self.c2.is_correct)


class TagModelTest(TestCase):
    def test_str_returns_name(self):
        tag = Tag.objects.create(name="Django")
        self.assertEqual(str(tag), "Django")

    def test_unique_name_constraint(self):
        Tag.objects.create(name="UniqueTag")
        with self.assertRaises(IntegrityError):
            Tag.objects.create(name="UniqueTag")


class ReviewModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="rev@example.com", username="rev", password="pass"
        )
        StudentProfile.objects.create(user=self.user)
        inst = User.objects.create_user(
            email="instrev@example.com", username="instrev", password="pass"
        )
        InstructorProfile.objects.create(user=inst)
        self.course = Course.objects.create(
            title="RCourse", description="RC", price=0, instructor=inst
        )

    def test_create_and_str(self):
        rev = Review.objects.create(
            user=self.user, course=self.course, rating=5, text="Great!"
        )
        self.assertEqual(str(rev), f"{self.user.email} → {self.course.title}: 5⭐")

    def test_unique_review_per_user_course(self):
        Review.objects.create(user=self.user, course=self.course, rating=4)
        with self.assertRaises(IntegrityError):
            Review.objects.create(user=self.user, course=self.course, rating=3)

    def test_course_average_rating(self):
        Review.objects.create(user=self.user, course=self.course, rating=4)
        another = User.objects.create_user(
            email="rev2@example.com", username="rev2", password="pass"
        )
        StudentProfile.objects.create(user=another)
        Review.objects.create(user=another, course=self.course, rating=2)
        self.assertEqual(self.course.average_rating, 3.0)


class WishlistItemModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="wish@example.com", username="wish", password="pass"
        )
        StudentProfile.objects.create(user=self.user)
        inst = User.objects.create_user(
            email="instwish@example.com", username="instwish", password="pass"
        )
        InstructorProfile.objects.create(user=inst)
        self.course = Course.objects.create(
            title="WCourse", description="WC", price=0, instructor=inst
        )

    def test_wishlist_creation_and_unique(self):
        item = WishlistItem.objects.create(user=self.user, course=self.course)
        self.assertTrue(WishlistItem.objects.filter(pk=item.pk).exists())
        with self.assertRaises(IntegrityError):
            WishlistItem.objects.create(user=self.user, course=self.course)


class PromotionModelTest(TestCase):
    def setUp(self):
        inst = User.objects.create_user(
            email="instpromo@example.com", username="instpromo", password="pass"
        )
        InstructorProfile.objects.create(user=inst)
        self.course = Course.objects.create(
            title="PCourse", description="PC", price=100, instructor=inst
        )
        self.promo = Promotion.objects.create(
            course=self.course,
            discount_percent=25,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=7)
        )

    def test_str_returns_discount_and_course(self):
        expected = f"25% off {self.course.title}"
        self.assertEqual(str(self.promo), expected)

    def test_promotion_dates(self):
        self.assertTrue(self.promo.start_date < self.promo.end_date)
