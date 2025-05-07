from rest_framework import permissions
from .models import Enrollment
from courses.models import Course

class IsEnrolled(permissions.BasePermission):
    """
    Allows access if the user is:
     - the instructor of the course
     - enrolled in the course
    """
    def has_object_permission(self, request, view, obj):
        user = request.user
        # instructors always allowed
        if hasattr(obj, "instructor") and obj.instructor == user:
            return True

        # resolve the course
        if isinstance(obj, Course):
            course = obj
        elif hasattr(obj, "course"):
            course = obj.course
        elif hasattr(obj, "lesson"):
           course = obj.lesson.course
        elif hasattr(obj, "package"):
            # scorm_package → its Course
            course = obj.package.course
        else:
            return False

        return Enrollment.objects.filter(user=user, course=course).exists()