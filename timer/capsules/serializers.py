from rest_framework import serializers
from .models import Capsule


class CapsuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Capsule
        fields = "__all__"
        read_only_fields = ["id", "owner", "status", "created_at"]

    def create(self, validated_data):
        # Automatically set the capsule status to LOCKED
        validated_data["status"] = "LOCKED"
        return super().create(validated_data)
