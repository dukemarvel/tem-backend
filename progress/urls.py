app_name = "progress"
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    LessonProgressViewSet,
    CourseProgressViewSet,
    ScormPackageProgressViewSet,
    CertificationViewSet,
    ScormCertificationViewSet,
)

router = DefaultRouter()
router.register("lessons", LessonProgressViewSet, basename="lesson-progress")
router.register("courses", CourseProgressViewSet, basename="course-progress")
router.register("scorm",   ScormPackageProgressViewSet, basename="scorm-progress")
router.register("certs",      CertificationViewSet,        basename="certification")
router.register("scorm-certs",ScormCertificationViewSet,   basename="scorm-certification")

urlpatterns = [
    path("", include(router.urls)),
]
