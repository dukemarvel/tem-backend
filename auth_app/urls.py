app_name = "auth_app"

from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView,
)
from .views import RegisterView, MeView, GoogleLogin

urlpatterns = [
    path("register/", RegisterView.as_view(), name="auth-register"),
    path("login/", TokenObtainPairView.as_view(), name="auth-login"),
    path("refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("logout/", TokenBlacklistView.as_view(), name="token-blacklist"),
    path("me/", MeView.as_view(), name="auth-me"),
    path("google/", GoogleLogin.as_view(), name="google-login"),
]
