from rest_framework import serializers
from .models import Capsule
from django.utils import timezone


class CapsuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Capsule
        fields = ("id", "owner", "title", "message", "file", "release_date", "status", "created_at")

    def create(self, validated_data):
        # Automatically set the capsule status to LOCKED
        validated_data["status"] = "LOCKED"
        return super().create(validated_data)
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        if not instance.can_be_opened():
            data['content'] = "🔒 This capsule is locked until release date."
            data['file'] = None
        return data
