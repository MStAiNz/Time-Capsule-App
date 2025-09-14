from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import viewsets, permissions
from .models import Capsule
from .serializers import CapsuleSerializer
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CapsuleForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login


class CapsuleViewSet(viewsets.ModelViewSet):
    serializer_class = CapsuleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Users can only see their own capsules
        return Capsule.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        # Save capsule with the current user as owner
        serializer.save(owner=self.request.user)

def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Signed up and logged in.")
            return redirect("capsule:my_capsules")
    else:
        form = UserCreationForm()
    return render(request, "registration/signup.html", {"form": form})

@login_required
def create_capsule(request):
    if request.method == "POST":
        form = CapsuleForm(request.POST, request.FILES)
        if form.is_valid():
            capsule = form.save(commit=False)
            capsule.owner = request.user
            # release_date from the form is likely naive; you may want to localize it
            capsule.save()
            messages.success(request, "Capsule saved and locked until release date.")
            return redirect("capsule:my_capsules")
    else:
        form = CapsuleForm()
    return render(request, "capsule/create_capsule.html", {"form": form})


@login_required
def my_capsules(request):
    capsules = Capsule.objects.filter(owner=request.user).order_by("-created_at")
    return render(request, "capsule/my_capsules.html", {"capsules": capsules})


@login_required
def view_capsule(request, pk):
    capsule = get_object_or_404(Capsule, pk=pk, owner=request.user)
    if capsule.can_be_opened():
        return render(request, "capsule/view_capsule.html", {"capsule": capsule})
    return render(request, "capsule/locked.html", {"capsule": capsule})

