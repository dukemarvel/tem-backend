from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import PaymentTransaction

@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True)
def send_payment_receipt(self, transaction_id):
    trx = PaymentTransaction.objects.get(pk=transaction_id)
    # send a simple receipt email
    send_mail(
        subject=f"Your payment for {trx.course.title} succeeded",
        message=(
            f"Hi {trx.user.username},\n\n"
            f"Thanks for your payment of ₦{trx.amount/100:.2f} for “{trx.course.title}”.\n"
            f"Reference: {trx.reference}\n\n"
            "Happy learning!\n"
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[trx.user.email],
    )
