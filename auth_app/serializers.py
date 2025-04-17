from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, InstructorProfile, StudentProfile

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    role = serializers.ChoiceField(
        choices=(("student", "Student"), ("instructor", "Instructor")),
        write_only=True
    )

    class Meta:
        model = User
        fields = ("email", "username", "password", "role")

    def create(self, validated_data):
        role = validated_data.pop("role")
        user = User.objects.create_user(**validated_data)
        if role == "instructor":
            InstructorProfile.objects.create(user=user)
        else:
            StudentProfile.objects.create(user=user)
        return user

class UserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "email", "username", "role")

    def get_role(self, obj):
        if hasattr(obj, "instructorprofile"):
            return "instructor"
        if hasattr(obj, "studentprofile"):
            return "student"
        return None
