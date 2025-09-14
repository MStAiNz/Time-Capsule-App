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
]