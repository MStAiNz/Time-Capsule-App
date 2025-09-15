from rest_framework import generics, permissions
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, render, redirect
from .serializers import RegisterSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
import requests
from django.conf import settings


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        # Send verification email
        token = RefreshToken.for_user(user).access_token
        verify_link = f'http://127.0.0.1:8000/api/auth/verify/{token}/'
        send_mail(
            'Verify Your Account',
            f'Click to Verify: {verify_link}'
            'no-reply@timecapsule.com',
            [user.email]
        )

    def signup_view(request):
        if request.method == "POST":
            form = RegisterSerializer(request.POST)
            if form.is_valid():
                form.save()
                return redirect("login")  # redirect to login after signup
        else:
            form = RegisterSerializer()
        return render(request, "registration/signup.html", {"form": form})
    

       
class VerifyEmailView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, token):
        from rest_framework_simplejwt.tokens import AccessToken
        try:
            access_token = AccessToken(token)
            user = get_object_or_404(User, id=access_token['user_id'])
            user.is_active = True
            user.save()
            return Response({'message': 'Email verified, you can now log in.'})
        except Exception:
            return Response({'error': 'Invalid or expired token'}, status=400)
    
class PasswordResetRequestView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        user = get_object_or_404(User, email=email)
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_link = f"http://127.0.0.1:8000/api/auth/reset/{uid}/{token}/"
        send_mail("Password Reset", f"Click to reset: {reset_link}",
                  "no-reply@timecapsule.com", [user.email])
        return Response({"message": "Password reset link sent"})
    
class PasswordResetConfirmView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, uid, token):
        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id)
            if default_token_generator.check_token(user, token):
                user.set_password(request.data.get("new_password"))
                user.save()
                return Response({"message": "Password reset successful"})
            else:
                return Response({"error": "Invalid token"}, status=400)
        except Exception:
            return Response({"error": "Invalid request"}, status=400)