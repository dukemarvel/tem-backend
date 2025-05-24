from rest_framework.routers import DefaultRouter
from .views import (
    OrganizationViewSet,
    TeamMemberViewSet,
    BulkPurchaseViewSet
)

router = DefaultRouter()
router.register("organizations", OrganizationViewSet)
router.register("members", TeamMemberViewSet)
router.register("purchases", BulkPurchaseViewSet)

urlpatterns = router.urls
