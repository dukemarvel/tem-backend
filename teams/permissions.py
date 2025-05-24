from rest_framework import permissions
from .models import TeamMember, Organization

class IsTeamAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        org_id = view.kwargs.get("pk") or request.data.get("organization")
        return Organization.objects.filter(pk=org_id, admin=request.user).exists()

class IsTeamMember(permissions.BasePermission):
    def has_permission(self, request, view):
        org_id = view.kwargs.get("organization") or request.data.get("organization")
        return TeamMember.objects.filter(
            organization_id=org_id,
            user=request.user,
            status="active"
        ).exists()
