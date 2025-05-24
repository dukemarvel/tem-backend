import uuid
from paystackapi.paystack import Paystack
from django.conf import settings
from .models import BulkPaymentTransaction
from courses.models import Course

paystack = Paystack(secret_key=settings.PAYSTACK_SECRET_KEY)

def process_team_checkout(data: dict, user) -> str:
    org_id = data["organization"]
    seats  = int(data["seats"])
    course_ids = data["courses"]
    courses = Course.objects.filter(id__in=course_ids)
    # compute total in kobo
    total = sum(int(c.price * 100) * seats for c in courses)

    reference = uuid.uuid4().hex
    trx = BulkPaymentTransaction.objects.create(
        organization_id=org_id,
        user=user,
        seats=seats,
        reference=reference,
        amount=total,
    )
    trx.courses.set(courses)

    # initialize Paystack
    init = paystack.transaction.initialize(
        amount=total,
        email=user.email,
        reference=reference,
        callback_url=settings.PAYSTACK_CALLBACK_URL,
    )
    return reference
