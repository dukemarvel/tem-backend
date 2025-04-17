from rest_framework import serializers
from .models import Course, Lesson

class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ["id", "title", "content", "video_url", "order", "created_at"]

class CourseSerializer(serializers.ModelSerializer):
    # Show lessons nested (read‑only by default for listing)
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ["id", "title", "description", "price", "instructor", "created_at", "lessons"]
        read_only_fields = ["instructor", "created_at"]

    def create(self, validated_data):
        # We’ll fill in `instructor` from request in the view
        return Course.objects.create(**validated_data)
