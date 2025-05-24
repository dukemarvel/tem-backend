from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import PaymentTransaction, BulkPaymentTransaction
from .tasks import send_payment_receipt, send_bulk_receipt, provision_team_seats

@receiver(post_save, sender=PaymentTransaction)
def on_payment_success(sender, instance, created, **kwargs):
    # only when status flips to “success”
    if not created and instance.status == "success":
        send_payment_receipt.delay(instance.id)



@receiver(post_save, sender=BulkPaymentTransaction)
def on_bulk_payment(sender, instance, created, **kwargs):
    if not created and instance.status == "success":
        send_bulk_receipt.delay(instance.id)
        provision_team_seats.delay(instance.id)