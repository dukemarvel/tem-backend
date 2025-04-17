app_name = "courses"

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CourseViewSet, LessonViewSet

router = DefaultRouter()
router.register("lessons", LessonViewSet, basename="lessons")
router.register("", CourseViewSet, basename="courses")


urlpatterns = [
    path("", include(router.urls)),
]