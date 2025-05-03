from rest_framework import serializers
from courses.models import Course

class InitTransactionSerializer(serializers.Serializer):
    course_id = serializers.IntegerField()

    def validate_course_id(self, value):
        try:
            self.course = Course.objects.get(pk=value)
        except Course.DoesNotExist:
            raise serializers.ValidationError("Course not found.")
        return value

class VerifyTransactionSerializer(serializers.Serializer):
    reference = serializers.CharField()
