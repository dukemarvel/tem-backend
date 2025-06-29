from rest_framework import serializers
from dj_rest_auth.registration.serializers import RegisterSerializer
from .models import Organization, TeamMember, BulkPurchase, TeamAnalyticsSnapshot


class TeamRegisterSerializer(RegisterSerializer):
    username = None
    first_name            = serializers.CharField()
    last_name             = serializers.CharField()
    company_name          = serializers.CharField()
    job_title             = serializers.CharField()
    company_size          = serializers.IntegerField()
    team_size             = serializers.IntegerField()
    heard_about           = serializers.CharField(allow_blank=True)
    organizational_needs  = serializers.CharField(allow_blank=True)

    def get_cleaned_data(self):
        data = super().get_cleaned_data()
        data.update({
            "first_name": self.validated_data.get("first_name"),
            "last_name":  self.validated_data.get("last_name"),
            "company_name":         self.validated_data.get("company_name"),
            "job_title":            self.validated_data.get("job_title"),
            "company_size":         self.validated_data.get("company_size"),
            "team_size":            self.validated_data.get("team_size"),
            "heard_about":          self.validated_data.get("heard_about"),
            "organizational_needs": self.validated_data.get("organizational_needs"),
        })
        return data

    def save(self, request):
        # 1) create the user
        user = super().save(request)

        # 2) create the org
        org = Organization.objects.create(
            name=self.cleaned_data["company_name"],
            admin=user,
            company_size=self.cleaned_data["company_size"],
            team_size=self.cleaned_data["team_size"],
            heard_about=self.cleaned_data["heard_about"],
            organizational_needs=self.cleaned_data["organizational_needs"],
        )

        # 3) add the user/founder as an active member
        TeamMember.objects.create(
            organization=org,
            user=user,
            invited_by=user,
            status=TeamMember.ACTIVE
        )

        return user

class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ["id","name","admin","created_at"]
        read_only_fields = ["admin","created_at"]

class TeamMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamMember
        fields = ["id","organization","user","status","invited_at","joined_at"]
        read_only_fields = ["invited_by","invited_at","joined_at","status"]

class BulkPurchaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = BulkPurchase
        fields = ["id","organization","seats","courses","order_reference","purchased_at"]
        read_only_fields = ["purchased_by","order_reference","purchased_at"]

class TeamAnalyticsSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamAnalyticsSnapshot
        fields = ["snapshot_at", "seat_usage", "learning_progress"]
        read_only_fields = fields