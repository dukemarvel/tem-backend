app_name = "courses"

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CourseViewSet, LessonViewSet, QuizViewSet, QuizSubmissionView

router = DefaultRouter()
router.register("quizzes", QuizViewSet, basename="quizzes")
router.register("quizzesubmit", QuizSubmissionView, basename="quizzesubmit")
router.register("lessons", LessonViewSet, basename="lessons")
router.register("", CourseViewSet, basename="courses")

urlpatterns = [
    path("", include(router.urls)),
]