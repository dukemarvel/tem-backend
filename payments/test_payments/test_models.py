from django.test import TestCase
from django.contrib.auth import get_user_model
from courses.models import Course
from teams.models import Organization
from payments.models import BulkPaymentTransaction, PaymentTransaction, Enrollment
from django.db import IntegrityError
from decimal import Decimal

User = get_user_model()

class PaymentModelsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="u@example.com", username="u", password="pass"
        )
        self.course = Course.objects.create(
            title="C", description="D", price=Decimal("20.00"), instructor=self.user
        )
        self.org = Organization.objects.create(
            name="Org1", admin=self.user
        )

    def test_bulk_paymenttransaction_str(self):
        # amount=4000 kobo → ₦40.00
        trx = BulkPaymentTransaction.objects.create(
            organization=self.org,
            user=self.user,
            seats=2,
            reference="ref1",
            amount=4000,
        )
        trx.courses.set([self.course])
        s = str(trx)
        self.assertIn(self.org.name, s)
        self.assertIn(trx.reference, s)
        self.assertIn("₦40.00", s)

    def test_bulk_payment_reference_unique(self):
        BulkPaymentTransaction.objects.create(
            organization=self.org, user=self.user,
            seats=1, reference="ref2", amount=1000
        )
        with self.assertRaises(IntegrityError):
            BulkPaymentTransaction.objects.create(
                organization=self.org, user=self.user,
                seats=1, reference="ref2", amount=1000
            )

    def test_paymenttransaction_str(self):
        trx = PaymentTransaction.objects.create(
            user=self.user, course=self.course,
            reference="ref123", amount=2000
        )
        s = str(trx)
        self.assertIn(self.user.email, s)
        self.assertIn(self.course.title, s)
        self.assertIn(trx.reference, s)

    def test_enrollment_str(self):
        enr = Enrollment.objects.create(user=self.user, course=self.course)
        self.assertEqual(
            str(enr),
            f"{self.user.email} enrolled in {self.course.title}"
        )

    def test_enrollment_unique_constraint(self):
        Enrollment.objects.create(user=self.user, course=self.course)
        with self.assertRaises(IntegrityError):
            Enrollment.objects.create(user=self.user, course=self.course)