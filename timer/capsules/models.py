from django.db import models
import uuid
from django.contrib.auth.models import User
from django.utils import timezone
from django_celery_beat.models import PeriodicTask, ClockedSchedule
import json


# Create your models here.
class Capsule(models.Model):
    STATUS_CHOICES = [
        ("LOCKED", "Locked"),
        ("UNLOCKED", "Unlocked"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="capsules")
    title = models.CharField(max_length=200)
    message = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to="capsules/", blank=True, null=True)
    release_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_public = models.BooleanField(default=False)
    status = models.CharField(
        max_length=20,
        choices=(("LOCKED", "Locked"), ("UNLOCKED", "Unlocked")),
        default="LOCKED",
    )

    def can_be_opened(self):
        return timezone.now() >= self.release_date
    
    def save(self, *args, **kwargs):
        # Auto-update status when saving
        self.status = "UNLOCKED" if self.can_be_opened() else "LOCKED"
        super().save(*args, **kwargs)
 
    def save(self, *args, **kwargs):
        new_capsule = self.pk is None
        super().save(*args, **kwargs)

        # Schedule Celery task at release_date
        if new_capsule:
            from .tasks import unlock_capsule
            from django_celery_beat.models import ClockedSchedule, PeriodicTask

            clocked, _ = ClockedSchedule.objects.get_or_create(clocked_time=self.release_date)
            PeriodicTask.objects.create(
                clocked=clocked,
                name=f"unlock_capsule_{self.id}",
                task="capsules.tasks.unlock_capsule",
                args=json.dumps([self.id]),
                one_off=True,
            )

    def unlock(self):
        self.status = "UNLOCKED"
        self.save()

    def __str__(self):
        return f"{self.title} - {self.owner.username}"
    
    @property
    def share_link(self):
        return f"/capsule/share/{self.share_uuid}/"