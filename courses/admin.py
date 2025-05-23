from django.contrib import admin

from .models import Course

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "instructor", "featured", "created_at")
    list_editable = ("featured",)
    list_filter = ("featured", "difficulty", "tags")
