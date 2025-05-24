from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import PaymentTransaction, BulkPaymentTransaction, Enrollment
from teams.models import TeamMember

@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True)
def send_payment_receipt(self, transaction_id):
    trx = PaymentTransaction.objects.get(pk=transaction_id)
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

@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True)
def send_bulk_receipt(self, transaction_id):
    trx = BulkPaymentTransaction.objects.get(pk=transaction_id)
    admin_email = trx.organization.admin.email
    total_amount = trx.amount / 100
    send_mail(
        subject=f"Bulk purchase confirmed for {trx.organization.name}",
        message=(
            f"Hi {trx.organization.admin.username},\n\n"
            f"Your bulk purchase of {trx.seats} seats for "
            f"{', '.join(c.title for c in trx.courses.all())} has succeeded.\n"
            f"Total paid: ₦{total_amount:.2f}\n"
            f"Reference: {trx.reference}\n\n"
            "Invitations have been provisioned for your team members.\n"
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[admin_email],
    )

@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True)
def provision_team_seats(self, transaction_id):
    trx = BulkPaymentTransaction.objects.get(pk=transaction_id)
    # find all active team members
    active_members = TeamMember.objects.filter(
        organization=trx.organization,
        status=TeamMember.ACTIVE
    )
    for member in active_members:
        for course in trx.courses.all():
            Enrollment.objects.get_or_create(
                user=member.user,
                course=course
            )
