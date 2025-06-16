from rest_framework import permissions
from .models import Enrollment
from courses.models import Course

class IsEnrolled(permissions.BasePermission):
    """
    Allows access when the requester is:
      • the instructor of the course, OR
      • enrolled and their access has not expired
    """
    def has_object_permission(self, request, view, obj):
        user = request.user

        # ―― 1) Instructors always sail through ―――――――――――――――――――――――――――
        if hasattr(obj, "instructor") and obj.instructor == user:
            return True

        # ―― 2) Work out which course this object belongs to ―――――――――――――――
        if isinstance(obj, Course):
            course = obj
        elif hasattr(obj, "course"):
            course = obj.course
        elif hasattr(obj, "lesson"):
            course = obj.lesson.course
        elif hasattr(obj, "package"):
            course = obj.package.course
        else:
            return False

        # ―― 3) Fetch the enrollment and check *is_active* ――――――――――――――――――
        enrollment = Enrollment.objects.filter(user=user, course=course).first()
        return bool(enrollment and enrollment.is_active)
