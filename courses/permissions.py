from rest_framework import permissions

class IsInstructor(permissions.BasePermission):
    """
    Allows access only to users with an instructor profile.
    """
    def has_permission(self, request, view):
        return (
            request.user 
            and request.user.is_authenticated 
            and hasattr(request.user, "instructorprofile")
        )


class IsOwnerInstructor(permissions.BasePermission):
    """
    Object‑level: only the instructor who owns the Course (or Lesson) may edit.
    """
    def has_object_permission(self, request, view, obj):
        # Course → obj.instructor
        if hasattr(obj, "instructor"):
            return obj.instructor == request.user
        # Lesson → obj.course.instructor
        if hasattr(obj, "course"):
            return obj.course.instructor == request.user
        # Quiz → obj.lesson.course.instructor
        if hasattr(obj, "lesson"):
            return obj.lesson.course.instructor == request.user
        return False