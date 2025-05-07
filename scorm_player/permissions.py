from rest_framework import permissions

class IsCourseInstructor(permissions.BasePermission):
    def has_permission(self, request, view):
        course_id = request.data.get("course") or view.kwargs.get("course_id")
        if not course_id:
            return False
        from courses.models import Course
        course = Course.objects.filter(pk=course_id).first()
        return course and course.instructor == request.user
