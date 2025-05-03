from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import PaymentTransaction
from .tasks import send_payment_receipt

@receiver(post_save, sender=PaymentTransaction)
def on_payment_success(sender, instance, created, **kwargs):
    # only when status flips to “success”
    if not created and instance.status == "success":
        send_payment_receipt.delay(instance.id)
