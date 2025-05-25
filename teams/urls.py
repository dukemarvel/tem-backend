from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    OrganizationViewSet,
    TeamMemberViewSet,
    BulkPurchaseViewSet
)

app_name = "teams"

router = DefaultRouter()
router.register("organizations", OrganizationViewSet)
router.register("members", TeamMemberViewSet)
router.register("purchases", BulkPurchaseViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
