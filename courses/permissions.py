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
