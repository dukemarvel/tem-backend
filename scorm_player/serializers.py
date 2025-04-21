from rest_framework import serializers
from .models import ScormPackage, Sco, RuntimeData

class ScormPackageUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScormPackage
        fields = ["id", "title", "file", "version"]

class ScoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sco
        fields = ["id", "title", "launch_url", "sequence"]

class RuntimeDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = RuntimeData
        fields = ["id", "sco", "attempt", "data", "updated_at"]
        read_only_fields = ["id", "sco", "attempt", "updated_at"]