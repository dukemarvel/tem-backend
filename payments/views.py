from django.utils import timezone
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from paystackapi.paystack import Paystack
from django.conf import settings
from .models import PaymentTransaction, Enrollment, BulkPaymentTransaction
from .serializers import InitTransactionSerializer, VerifyTransactionSerializer
from .services import process_team_checkout
from .serializers import InitTeamTransactionSerializer, VerifyTeamTransactionSerializer
from courses.models import Course
import uuid
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied
import hashlib, hmac, json
from datetime import timedelta

paystack = Paystack(secret_key=settings.PAYSTACK_SECRET_KEY)

class InitializeTransactionAPIView(generics.GenericAPIView):
    serializer_class = InitTransactionSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        course = Course.objects.get(pk=serializer.validated_data["course_id"])
        amount_kobo = int(course.price * 100)

        # generate our own unique reference
        reference = uuid.uuid4().hex

        # create pending transaction
        trx = PaymentTransaction.objects.create(
            user=request.user,
            course=course,
            amount=amount_kobo,
            reference=reference,
        )

        # call Paystack initialize
        init_response = paystack.transaction.initialize(
            amount=amount_kobo,
            email=request.user.email,
            reference=reference,
            callback_url=settings.PAYSTACK_CALLBACK_URL,
        )
        auth_url = init_response.get("data", {}).get("authorization_url")
        return Response({
            "authorization_url": auth_url,
            "reference": reference
        }, status=status.HTTP_200_OK)

class VerifyTransactionAPIView(generics.GenericAPIView):
    serializer_class = VerifyTransactionSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        ref = request.data.get("reference")
        trx = PaymentTransaction.objects.get(reference=ref)
        verify_resp = paystack.transaction.verify(reference=ref)
        data = verify_resp.get("data", {})
        status_str = data.get("status")

        trx.status = "success" if status_str == "success" else "failed"
        if trx.status == "success":
            trx.paid_at = timezone.now()

            # --- determine expiry ----------------------------
            course = trx.course
            days   = course.default_access_days  # None → lifetime
            expires = timezone.now() + timedelta(days=days) if days else None
            # --------------------------------------------------

            Enrollment.objects.get_or_create(user=trx.user, 
                                             course=trx.course,
                                             defaults = {"access_expires": expires})
        trx.save()

        return Response({"status": trx.status}, status=status.HTTP_200_OK)



class PaystackWebhookAPIView(APIView):
    authentication_classes = ()   # Paystack will sign with secret, not a JWT
    permission_classes = ()
    # disable CSRF
    def post(self, request, *args, **kwargs):
        signature = request.META.get("HTTP_X_PAYSTACK_SIGNATURE", "")
        secret = settings.PAYSTACK_SECRET_KEY.encode()
        body = request.body
        expected = hmac.new(secret, body, hashlib.sha512).hexdigest()
        if not hmac.compare_digest(expected, signature):
            raise PermissionDenied("Invalid signature")

        event = json.loads(body)
        if event["event"] == "charge.success":
            ref = event["data"]["reference"]
            try:
                trx = PaymentTransaction.objects.get(reference=ref)
                if trx.status != "success":
                    trx.status = "success"
                    trx.paid_at = timezone.now()
                    trx.save()
                    #Enrollment.objects.get_or_create(user=trx.user, course=trx.course)
                    course  = trx.course
                    days    = course.default_access_days
                    expires = timezone.now() + timedelta(days=days) if days else None

                    Enrollment.objects.get_or_create( 
                        user=trx.user, 
                        course=course, 
                        defaults={"access_expires": expires}, 
                    )

            except PaymentTransaction.DoesNotExist:
                pass

        return Response({"received": True})
    

class InitializeTeamTransactionAPIView(generics.GenericAPIView):
    serializer_class = InitTeamTransactionSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        s = self.get_serializer(data=request.data)
        s.is_valid(raise_exception=True)
        ref = process_team_checkout(request.data, request.user)
        return Response({"reference": ref}, status=status.HTTP_200_OK)

class VerifyTeamTransactionAPIView(generics.GenericAPIView):
    serializer_class = VerifyTeamTransactionSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        ref = request.data.get("reference")
        trx = BulkPaymentTransaction.objects.get(reference=ref)
        verify = paystack.transaction.verify(reference=ref).get("data", {})
        if verify.get("status") == "success":
            trx.status = "success"
            trx.paid_at = timezone.now()
            trx.save()
            # you can signal/post-process seat provisioning here
        else:
            trx.status = "failed"
            trx.save()
        return Response({"status": trx.status}, status=status.HTTP_200_OK)