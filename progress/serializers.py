from rest_framework import serializers
from .models import LessonProgress, CourseProgress, ScormPackageProgress, Certification, ScormCertification

class LessonProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model  = LessonProgress
        fields = ["id","user","lesson","is_completed","updated_at"]
        read_only_fields = ["id", "user", "updated_at"]

class CourseProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model  = CourseProgress
        fields = ["id","user","course","percent","updated_at"]
        read_only_fields = ["id", "user", "percent", "updated_at"]

class ScormPackageProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model  = ScormPackageProgress
        fields = ["id","user","package","percent","updated_at"]
        read_only_fields = ["id", "user", "percent", "updated_at"]



class CertificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certification
        fields = ["id", "lesson", "cert_id", "issued_at"]

class ScormCertificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScormCertification
        fields = ["id", "package", "cert_id", "issued_at"]