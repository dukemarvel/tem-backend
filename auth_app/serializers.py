from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import UserDetailsSerializer
from rest_framework import serializers
from .models import StudentProfile, InstructorProfile

class CustomRegisterSerializer(RegisterSerializer):
    username = None                      # ④  suppress inherited field
    first_name = serializers.CharField()
    last_name  = serializers.CharField()
    avatar     = serializers.ImageField(required=False, allow_null=True)

    role = serializers.ChoiceField(
        choices=[("student", "Student"), ("instructor", "Instructor")],
        write_only=True,
    )

    def get_cleaned_data(self):
        data = super().get_cleaned_data()
        data.update(
            first_name = self.validated_data.get("first_name"),
            last_name  = self.validated_data.get("last_name"),
            avatar     = self.validated_data.get("avatar"),
            role       = self.validated_data.get("role"),
        )
        return data

    def save(self, request):
        user = super().save(request)
        role = self.cleaned_data["role"]
        if role == "instructor":
            InstructorProfile.objects.create(user=user)
        else:
            StudentProfile.objects.create(user=user)
        return user


class CustomUserDetailsSerializer(UserDetailsSerializer):
    role = serializers.SerializerMethodField()

    class Meta(UserDetailsSerializer.Meta):
        fields = ("id", "email", "first_name", "last_name", "avatar", "role")

    def get_role(self, obj):
        if hasattr(obj, "instructorprofile"):
            return "instructor"
        if hasattr(obj, "studentprofile"):
            return "student"
        return None