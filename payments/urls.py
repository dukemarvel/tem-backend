from django.urls import path
from .views import (
    InitializeTransactionAPIView,
    VerifyTransactionAPIView,
    PaystackWebhookAPIView,
    InitializeTeamTransactionAPIView,
    VerifyTeamTransactionAPIView
)

app_name = "payments"

urlpatterns = [
    path("init/",   InitializeTransactionAPIView.as_view(), name="init-transaction"),
    path("verify/", VerifyTransactionAPIView.as_view(),   name="verify-transaction"),
    path("team/init/",   InitializeTeamTransactionAPIView.as_view(), name="team-init"),
    path("team/verify/", VerifyTeamTransactionAPIView.as_view(),  name="team-verify"),
    path("webhook/", PaystackWebhookAPIView.as_view(),    name="webhook"),
]
