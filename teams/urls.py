from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TeamRegisterView,
    TeamLoginView,
    OrganizationViewSet,
    TeamMemberViewSet,
    BulkPurchaseViewSet,
)

app_name = "teams"
router = DefaultRouter()
router.register("organizations", OrganizationViewSet)
router.register("members",       TeamMemberViewSet)
router.register("purchases",     BulkPurchaseViewSet)

urlpatterns = [
    # business signup & login
    path("register/", TeamRegisterView.as_view(), name="team-register"),
    path("login/",    TeamLoginView.as_view(),    name="team-login"),

    # all the rest of our /teams/... endpoints
    path("", include(router.urls)),
]