import json
import hmac
import hashlib
from django.test import TestCase
from django.conf import settings
from django.contrib.auth import get_user_model
from courses.models import Course
from payments.models import PaymentTransaction, Enrollment
from rest_framework.test import APIClient
from decimal import Decimal
from unittest.mock import patch

User = get_user_model()

class PaymentsViewsTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="a@test.com", username="a", password="pass"
        )
        # make the user both instructor and student for testing
        self.course = Course.objects.create(
            title="Ct",
            description="Desc",
            price=Decimal("10.00"),
            instructor=self.user,
        )
        self.client.force_authenticate(user=self.user)
        self.init_url = "/api/v1/payments/init/"
        self.verify_url = "/api/v1/payments/verify/"
        self.webhook_url = "/api/v1/payments/webhook/"

    @patch("payments.views.paystack.transaction.initialize")
    def test_initialize_transaction_success(self, mock_initialize):
        mock_initialize.return_value = {
            "data": {"authorization_url": "https://pay.test/authorize"}
        }
        resp = self.client.post(
            self.init_url, {"course_id": self.course.id}, format="json"
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["authorization_url"], "https://pay.test/authorize")
        self.assertIn("reference", data)
        trx = PaymentTransaction.objects.get(reference=data["reference"])
        self.assertEqual(trx.user, self.user)
        self.assertEqual(trx.course, self.course)
        # course price 10.00 → amount in kobo is 1000
        self.assertEqual(trx.amount, 1000)

    def test_initialize_transaction_unauthenticated(self):
        self.client.force_authenticate(user=None)
        resp = self.client.post(
            self.init_url, {"course_id": self.course.id}, format="json"
        )
        self.assertEqual(resp.status_code, 401)

    @patch("payments.views.paystack.transaction.verify")
    def test_verify_transaction_success(self, mock_verify):
        trx = PaymentTransaction.objects.create(
            user=self.user, course=self.course, reference="ref-x", amount=1000
        )
        mock_verify.return_value = {"data": {"status": "success"}}
        resp = self.client.post(self.verify_url, {"reference": "ref-x"}, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["status"], "success")
        trx.refresh_from_db()
        self.assertEqual(trx.status, "success")
        self.assertIsNotNone(trx.paid_at)
        self.assertTrue(
            Enrollment.objects.filter(user=self.user, course=self.course).exists()
        )

    @patch("payments.views.paystack.transaction.verify")
    def test_verify_transaction_failed(self, mock_verify):
        trx = PaymentTransaction.objects.create(
            user=self.user, course=self.course, reference="ref-y", amount=2000
        )
        mock_verify.return_value = {"data": {"status": "failed"}}
        resp = self.client.post(self.verify_url, {"reference": "ref-y"}, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["status"], "failed")
        trx.refresh_from_db()
        self.assertEqual(trx.status, "failed")
        self.assertFalse(
            Enrollment.objects.filter(user=self.user, course=self.course).exists()
        )

    def test_verify_transaction_unauthenticated(self):
        self.client.force_authenticate(user=None)
        resp = self.client.post(self.verify_url, {"reference": "whatever"}, format="json")
        self.assertEqual(resp.status_code, 401)

    def test_webhook_charge_success(self):
        trx = PaymentTransaction.objects.create(
            user=self.user, course=self.course, reference="ref-web", amount=1000
        )
        body = json.dumps(
            {"event": "charge.success", "data": {"reference": "ref-web"}}
        ).encode()
        signature = hmac.new(
            settings.PAYSTACK_SECRET_KEY.encode(), body, hashlib.sha512
        ).hexdigest()
        resp = self.client.post(
            self.webhook_url,
            data=body,
            content_type="application/json",
            HTTP_X_PAYSTACK_SIGNATURE=signature,
        )
        self.assertEqual(resp.status_code, 200)
        trx.refresh_from_db()
        self.assertEqual(trx.status, "success")
        self.assertIsNotNone(trx.paid_at)
        self.assertTrue(
            Enrollment.objects.filter(user=self.user, course=self.course).exists()
        )

    def test_webhook_invalid_signature(self):
        PaymentTransaction.objects.create(
            user=self.user, course=self.course, reference="ref-web2", amount=500
        )
        body = json.dumps(
            {"event": "charge.success", "data": {"reference": "ref-web2"}}
        ).encode()
        resp = self.client.post(
            self.webhook_url,
            data=body,
            content_type="application/json",
            HTTP_X_PAYSTACK_SIGNATURE="bad-signature",
        )
        self.assertEqual(resp.status_code, 403)

    def test_webhook_non_charge_event(self):
        trx = PaymentTransaction.objects.create(
            user=self.user, course=self.course, reference="ref-web3", amount=1000
        )
        body = json.dumps(
            {"event": "other.event", "data": {"reference": "ref-web3"}}
        ).encode()
        signature = hmac.new(
            settings.PAYSTACK_SECRET_KEY.encode(), body, hashlib.sha512
        ).hexdigest()
        resp = self.client.post(
            self.webhook_url,
            data=body,
            content_type="application/json",
            HTTP_X_PAYSTACK_SIGNATURE=signature,
        )
        self.assertEqual(resp.status_code, 200)
        trx.refresh_from_db()
        self.assertEqual(trx.status, "pending")
