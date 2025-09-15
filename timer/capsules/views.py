from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import viewsets, permissions
from .models import Capsule
from .serializers import CapsuleSerializer
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CapsuleForm
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login
import requests
from django.contrib.auth import authenticate
from django.conf import settings
from django.contrib.auth.decorators import login_required


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

def jwt_login(request):
        if request.method == "POST":
            form = AuthenticationForm(request, data=request.POST)
            if form.is_valid():
                username = form.cleaned_data.get("username")
                password = form.cleaned_data.get("password")

                # Call JWT endpoint
                response = requests.post(
                    request.build_absolute_uri("/api/token/"),
                    data={"username": username, "password": password}
                )

                if response.status_code == 200:
                    tokens = response.json()  # {"access": "...", "refresh": "..."}
                    request.session["access"] = tokens["access"]
                    request.session["refresh"] = tokens["refresh"]
                    return redirect("capsule:my_capsules")  # redirect to dashboard/home
                else:
                    form.add_error(None, "Invalid credentials for JWT.")
        else:
            form = AuthenticationForm()

        return render(request, "registration/login.html", {"form": form})

@login_required
def public_gallery(request):
    """List all public capsules (global feed)."""
    capsules = Capsule.objects.filter(is_public=True).order_by("-release_date")
    return render(request, "capsules/public_gallery.html", {"capsules": capsules})


@login_required
def capsule_share(request, uuid):
    """Access capsule via unique share link."""
    capsule = get_object_or_404(Capsule, share_uuid=uuid)

    # Allow if owner, contributor, or public
    if (
        capsule.is_public
        or capsule.owner == request.user
    ):
        return render(request, "capsules/capsule_detail.html", {"capsule": capsule})

    messages.error(request, "You don’t have permission to view this capsule.")
    return redirect("capsule:my_capsules")


@login_required
def create_capsule(request):
    if request.method == "POST":
        form = CapsuleForm(request.POST, request.FILES)
        if form.is_valid():
            capsule = form.save(commit=False)
            capsule.owner = request.user
            # release_date from the form is likely naive; you may want to localize it
            capsule.save()
            form.save_m2m()
            messages.success(request, "Capsule saved and locked until release date.")
            return redirect("capsule:detail", pk=capsule.pk)
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

@login_required
def capsule_dashboard(request):
    """Display user capsules with filters (upcoming, released, public)."""
    filter_by = request.GET.get("filter", "all")  # default = all
    now = timezone.now()

    # Base queryset
    capsules = Capsule.objects.filter(owner=request.user)

    # Apply filters
    if filter_by == "upcoming":
        capsules = capsules.filter(release_date__gt=now)
    elif filter_by == "released":
        capsules = capsules.filter(release_date__lte=now)
    elif filter_by == "public":
        capsules = Capsule.objects.filter(is_public=True)

    context = {
        "capsules": capsules,
        "filter_by": filter_by,
    }
    return render(request, "capsules/dashboard.html", context)

@login_required
def capsule_edit(request, pk):
    capsule = get_object_or_404(Capsule, pk=pk, owner=request.user)
    if request.method == "POST":
        form = CapsuleForm(request.POST, instance=capsule)
        if form.is_valid():
            form.save()
            messages.success(request, "Capsule updated successfully.")
            return redirect("capsule:detail", pk=capsule.pk)
    else:
        form = CapsuleForm(instance=capsule)

    return render(request, "capsules/capsule_form.html", {"form": form, "edit_mode": True})


@login_required
def capsule_delete(request, pk):
    capsule = get_object_or_404(Capsule, pk=pk, owner=request.user)
    if request.method == "POST":
        capsule.delete()
        messages.success(request, "Capsule deleted.")
        return redirect("capsule:my_capsules")
    return render(request, "capsules/capsule_confirm_delete.html", {"capsule": capsule})

def detail(request, pk):
    capsule = get_object_or_404(Capsule, pk=pk, owner=request.user)

    # Only owner or public capsules are accessible
    if capsule.owner != request.user and not capsule.is_public:
        messages.error(request, "You don’t have permission to view this capsule.")
        return redirect("capsule:my_capsules")
    
    return render(request, "capsules/detail.html", {"capsule": capsule})