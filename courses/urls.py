app_name = "courses"

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (CourseViewSet, LessonViewSet, QuizViewSet, 
                    ModuleViewSet, ReviewViewSet, PromotionViewSet, QuizSubmissionView, CategoryViewSet)

router = DefaultRouter()
router.register("modules", ModuleViewSet, basename="modules")
router.register("reviews", ReviewViewSet, basename="reviews")
router.register("promotions", PromotionViewSet, basename="promotions")
router.register("quizzes", QuizViewSet, basename="quizzes")
router.register("quizzesubmit", QuizSubmissionView, basename="quizzesubmit")
router.register("lessons", LessonViewSet, basename="lessons")
router.register("categories", CategoryViewSet, basename="categories")
router.register("", CourseViewSet, basename="courses")

urlpatterns = [
    path("", include(router.urls)),
]