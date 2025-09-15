from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from .models import Capsule

@shared_task
def unlock_capsule(capsule_id):
    try:
        capsule = Capsule.objects.get(id=capsule_id)
        if capsule.release_date <= timezone.now():
            capsule.unlock()
            # send notification email
            send_mail(
                subject="Your Time Capsule is Unlocked 🎉",
                message=f"Hello {capsule.owner.username},\n\n"
                        f"Your capsule '{capsule.title}' is now unlocked!\n"
                        f"Access it here: http://127.0.0.1:8000/capsules/{capsule.id}/",
                from_email="noreply@timecapsule.com",
                recipient_list=[capsule.owner.email],
                fail_silently=True,
            )
    except Capsule.DoesNotExist:
        pass
