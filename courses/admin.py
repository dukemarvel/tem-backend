from django.contrib import admin

from .models import Course, Category
from django.utils.html import format_html

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "instructor", "featured", "created_at")
    list_editable = ("featured",)
    list_filter = ("featured", "difficulty", "tags")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "subtitle", "image_tag", "parent")
    readonly_fields = ("image_tag",)

    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:40px;"/>', obj.image.url)
        return "-"
    image_tag.short_description = "Thumbnail"