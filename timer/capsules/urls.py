from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CapsuleViewSet
from . import views

router = DefaultRouter()
router.register(r'capsules', CapsuleViewSet, basename='capsule')

urlpatterns = [
    path('', include(router.urls)),
]

app_name = "capsule"

urlpatterns = [
    path("create/", views.create_capsule, name="create_capsule"),
    path("my/", views.my_capsules, name="my_capsules"),
    path("view/<int:pk>/", views.view_capsule, name="view_capsule"),
    path("dashboard/", views.capsule_dashboard, name="my_capsule"),
    path("gallery/", views.public_gallery, name="public_gallery"),
    path("share/<uuid:uuid>/", views.capsule_share, name="capsule_share"),
    path("new/", views.create_capsule, name="capsule_create"),
    path("<int:pk>/", views.detail, name="capsule_detail"),
    path("<int:pk>/edit/", views.capsule_edit, name="capsule_edit"),
    path("<int:pk>/delete/", views.capsule_delete, name="capsule_delete"),
]