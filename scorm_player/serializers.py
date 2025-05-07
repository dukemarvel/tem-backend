from rest_framework import serializers
from .models import ScormPackage, Sco, RuntimeData

class ScormPackageUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScormPackage
        fields = ["id", "title", "file", "course", "version"]


    def validate_course(self, course):
        # only the course’s instructor may attach a SCORM package
        user = self.context["request"].user
        if course.instructor != user:
            raise serializers.ValidationError("You do not own that course.")
        return course

class ScoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sco
        fields = ["id", "title", "launch_url", "sequence"]

class RuntimeDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = RuntimeData
        fields = ["id", "sco", "attempt", "data", "updated_at"]
        read_only_fields = ["id", "sco", "attempt", "updated_at"]