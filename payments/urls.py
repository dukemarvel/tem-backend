from django.urls import path
from .views import (
    InitializeTransactionAPIView,
    VerifyTransactionAPIView,
    PaystackWebhookAPIView,
)

app_name = "payments"

urlpatterns = [
    path("init/",   InitializeTransactionAPIView.as_view(), name="init-transaction"),
    path("verify/", VerifyTransactionAPIView.as_view(),   name="verify-transaction"),
    path("webhook/", PaystackWebhookAPIView.as_view(),    name="webhook"),
]
