from django.contrib import admin
from .models import LessonProgress, CourseProgress, ScormPackageProgress

@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display  = ("user", "lesson", "is_completed", "updated_at")
    list_filter   = ("is_completed",)
    search_fields = ("user__username","lesson__title")

@admin.register(CourseProgress)
class CourseProgressAdmin(admin.ModelAdmin):
    list_display  = ("user", "course", "percent", "updated_at")
    list_filter   = ("course",)
    search_fields = ("user__username","course__title")

@admin.register(ScormPackageProgress)
class ScormPackageProgressAdmin(admin.ModelAdmin):
    list_display  = ("user", "package", "percent", "updated_at")
    list_filter   = ("package",)
    search_fields = ("user__username","package__title")
