from django.test import TestCase
from django.contrib.auth import get_user_model
from courses.models import Course
from payments.serializers import InitTransactionSerializer, VerifyTransactionSerializer
from decimal import Decimal

User = get_user_model()

class PaymentsSerializersTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="ser@test.com", username="ser", password="pwd"
        )
        self.course = Course.objects.create(
            title="Ser Course",
            description="Desc",
            price=Decimal("5.00"),
            instructor=self.user,
        )

    def test_init_serializer_valid(self):
        serializer = InitTransactionSerializer(data={"course_id": self.course.id})
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["course_id"], self.course.id)
        # the custom validator sets `self.course`
        self.assertEqual(serializer.course, self.course)

    def test_init_serializer_invalid(self):
        serializer = InitTransactionSerializer(data={"course_id": 9999})
        self.assertFalse(serializer.is_valid())
        self.assertIn("course_id", serializer.errors)
        self.assertEqual(serializer.errors["course_id"][0], "Course not found.")

    def test_verify_serializer_valid(self):
        serializer = VerifyTransactionSerializer(data={"reference": "abc123"})
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["reference"], "abc123")

    def test_verify_serializer_missing(self):
        serializer = VerifyTransactionSerializer(data={})
        self.assertFalse(serializer.is_valid())
        self.assertIn("reference", serializer.errors)
