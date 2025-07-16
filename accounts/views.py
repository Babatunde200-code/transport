from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser
from .serializers import SignupSerializer, VerifyAccountSerializer, LoginSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from .models import UserProfile
from .serializers import UserProfileSerializer
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.contrib.auth.tokens import default_token_generator

class SignupView(APIView):
    permission_classes = [AllowAny]  

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Verification code sent to your email'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyAccountView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = VerifyAccountSerializer(data=request.data)
        if serializer.is_valid():
            user = CustomUser.objects.get(email=serializer.validated_data['email'])
            user.is_verified = True
            user.verification_code = ""
            user.save()
            return Response({"detail": "Account verified"})
        return Response(serializer.errors, status=400)

class LoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        return Response(serializer.errors, status=400)
    
## views for the users profile

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = request.user.profile
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)

    def put(self, request):
        profile = request.user.profile
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

class ProfilePhotoUploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        profile = request.user.profile
        profile.profile_photo = request.FILES.get('profile_photo')
        profile.save()
        return Response({"detail": "Profile photo updated."})


class PasswordResetRequestView(APIView):
    def post(self, request):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
            token = default_token_generator.make_token(user)
            reset_link = f"http://localhost:3000/reset-password/{user.pk}/{token}"
            
            send_mail(
                'Reset your password',
                f'Click the link to reset your password: {reset_link}',
                'no-reply@translink.com',
                [email],
            )
            return Response({"message": "Password reset link sent!"})
        except User.DoesNotExist:
            return Response({"error": "User with this email does not exist."}, status=404)
        
from django.contrib.auth.tokens import default_token_generator

class PasswordResetConfirmView(APIView):
    def post(self, request, uid, token):
        try:
            user = User.objects.get(pk=uid)
            if not default_token_generator.check_token(user, token):
                return Response({"error": "Invalid or expired token"}, status=400)
            
            password = request.data.get('password')
            user.set_password(password)
            user.save()
            return Response({"message": "Password reset successful"})
        except User.DoesNotExist:
            return Response({"error": "Invalid user ID"}, status=400)