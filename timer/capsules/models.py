from django.db import models
import uuid
from django.contrib.auth.models import User
from django.utils import timezone


# Create your models here.
class Capsule(models.Model):
    STATUS_CHOICES = [
        ("LOCKED", "Locked"),
        ("UNLOCKED", "Unlocked"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="capsules")
    title = models.CharField(max_length=200)
    message = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to="capsules/", blank=True, null=True)
    release_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="LOCKED")
    created_at = models.DateTimeField(auto_now_add=True)

    def can_be_opened(self):
        return timezone.now() >= self.release_date

    def __str__(self):
        return f"{self.title} - {self.owner.username}"