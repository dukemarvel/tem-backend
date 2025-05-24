from django.test import TestCase
from django.contrib.auth import get_user_model
from courses.models import Course
from teams.models import Organization
from payments.serializers import (
    InitTransactionSerializer, VerifyTransactionSerializer,
    InitTeamTransactionSerializer, VerifyTeamTransactionSerializer
)
from decimal import Decimal

User = get_user_model()

class PaymentsSerializersTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="ser@test.com", username="ser", password="pwd"
        )
        self.course = Course.objects.create(
            title="Ser Course", description="Desc",
            price=Decimal("5.00"), instructor=self.user
        )
        self.org = Organization.objects.create(
            name="OrgT", admin=self.user
        )

    # ---- individual payments ----
    def test_init_serializer_valid(self):
        ser = InitTransactionSerializer(data={"course_id": self.course.id})
        self.assertTrue(ser.is_valid())
        self.assertEqual(ser.validated_data["course_id"], self.course.id)
        self.assertEqual(ser.course, self.course)

    def test_init_serializer_invalid(self):
        ser = InitTransactionSerializer(data={"course_id": 9999})
        self.assertFalse(ser.is_valid())
        self.assertEqual(ser.errors["course_id"][0], "Course not found.")

    def test_verify_serializer_valid(self):
        ser = VerifyTransactionSerializer(data={"reference": "abc123"})
        self.assertTrue(ser.is_valid())
        self.assertEqual(ser.validated_data["reference"], "abc123")

    def test_verify_serializer_missing(self):
        ser = VerifyTransactionSerializer(data={})
        self.assertFalse(ser.is_valid())
        self.assertIn("reference", ser.errors)

    # ---- team payments ----
    def test_init_team_serializer_valid(self):
        data = {
            "organization": self.org.id,
            "seats": 3,
            "courses": [self.course.id]
        }
        ser = InitTeamTransactionSerializer(data=data)
        self.assertTrue(ser.is_valid(), ser.errors)
        self.assertEqual(ser.validated_data["organization"], self.org.id)
        self.assertEqual(ser.validated_data["seats"], 3)
        self.assertEqual(ser.validated_data["courses"], [self.course.id])

    def test_init_team_serializer_missing_fields(self):
        ser = InitTeamTransactionSerializer(data={})
        self.assertFalse(ser.is_valid())
        self.assertIn("organization", ser.errors)
        self.assertIn("seats", ser.errors)
        self.assertIn("courses", ser.errors)

    def test_verify_team_serializer_valid(self):
        ser = VerifyTeamTransactionSerializer(data={"reference": "teamref"})
        self.assertTrue(ser.is_valid())
        self.assertEqual(ser.validated_data["reference"], "teamref")

    def test_verify_team_serializer_missing(self):
        ser = VerifyTeamTransactionSerializer(data={})
        self.assertFalse(ser.is_valid())
        self.assertIn("reference", ser.errors)
