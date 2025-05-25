from rest_framework import serializers
from .models import Organization, TeamMember, BulkPurchase

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