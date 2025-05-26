from django.contrib.auth import get_user_model
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import (
    Organization, TeamMember, 
    BulkPurchase, TeamAnalyticsSnapshot)
from .serializers import (
    OrganizationSerializer, TeamMemberSerializer, 
    BulkPurchaseSerializer, TeamAnalyticsSnapshotSerializer
)
from .permissions import IsTeamAdmin, IsTeamMember
from payments.services import process_team_checkout

class OrganizationViewSet(viewsets.ModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer

    def perform_create(self, serializer):
        serializer.save(admin=self.request.user)

    @action(detail=True, methods=["get"], permission_classes=[IsTeamAdmin])
    def dashboard(self, request, pk=None):
        org = self.get_object()
        total_seats = sum(p.seats for p in org.purchases.all())
        used_seats  = org.members.filter(status="active").count()
        return Response({
            "total_seats": total_seats,
            "used_seats": used_seats,
            "pending_invites": org.members.filter(status="pending").count(),
        })
    
    @action(detail=True, methods=["get"], permission_classes=[IsTeamAdmin])
    def analytics(self, request, pk=None):
        """
        Return the latest pre-computed analytics snapshot.
        """
        org = self.get_object()
        snap = TeamAnalyticsSnapshot.objects.filter(
            organization=org
        ).order_by("-snapshot_at").first()

        if not snap:
            return Response(
                {"detail": "No analytics snapshot available."},
                status=status.HTTP_404_NOT_FOUND
            )

        data = TeamAnalyticsSnapshotSerializer(snap).data
        return Response(data)


class TeamMemberViewSet(viewsets.ModelViewSet):
    queryset = TeamMember.objects.all()
    serializer_class = TeamMemberSerializer

    def get_permissions(self):
        if self.action in ["create", "invite", "destroy"]:
            return [IsTeamAdmin()]
        return [IsTeamMember()]

    @action(detail=True, methods=["post"], url_path="invite")
    def invite(self, request, pk=None):
        org = Organization.objects.get(pk=pk)
        emails = request.data.get("emails", [])
        invited = []
        for email in emails:
            user = get_user_model().objects.get(email=email)
            tm, created = TeamMember.objects.get_or_create(
                organization=org,
                user=user,
                defaults={"invited_by": request.user}
            )
            invited.append({"email": email, "status": tm.status})
        return Response({"invited": invited}, status=status.HTTP_201_CREATED)


class BulkPurchaseViewSet(viewsets.ModelViewSet):
    queryset = BulkPurchase.objects.all()
    serializer_class = BulkPurchaseSerializer

    def get_permissions(self):
        if self.action in ["create"]:
            return [IsTeamAdmin()]
        return [IsTeamAdmin()]

    def perform_create(self, serializer):
        
        order_ref = process_team_checkout(self.request.data, self.request.user) 
        serializer.save(
            purchased_by=self.request.user,
            order_reference=order_ref
        )
