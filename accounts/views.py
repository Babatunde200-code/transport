import random
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.conf import settings

from .serializers import SignupSerializer
from .repository import UserRepository
from .auth_utils import users, hash_password, check_password, generate_jwt


# ---------------- Signup ----------------
class SignupView(APIView):
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        data = serializer.validated_data
        email = data["email"]
        password = data["password"]

        # Check if user exists
        if UserRepository.find_by_email(email):
            return Response({"error": "Email already exists"}, status=400)

        # Generate verification code
        verification_code = str(random.randint(100000, 999999))

        # Create user
        UserRepository.create_user({
            "email": email,
            "password": make_password(password),  # hash password
            "is_verified": False,
            "verification_code": verification_code,
        })

        # Send verification email
        try:
            send_mail(
                subject="Verify Your Account",
                message=f"Your verification code is {verification_code}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
        except Exception as e:
            return Response({"error": f"Failed to send email: {str(e)}"}, status=500)

        return Response({
            "message": "Signup successful. Please check your email for the verification code.",
            "email": email
        }, status=201)


# ---------------- Verify Account ----------------
class VerifyAccountView(APIView):
    def post(self, request):
        email = request.data.get("email")
        code = request.data.get("code")

        if not email or not code:
            return Response({"error": "Email and code are required"}, status=400)

        result = UserRepository.verify_user(email, code)
        if result.modified_count == 0:
            return Response({"error": "Invalid code or email"}, status=400)

        return Response({"message": "Account verified successfully"})


# ---------------- Resend Verification ----------------
class ResendVerificationView(APIView):
    def post(self, request):
        email = request.data.get("email")

        if not email:
            return Response({"error": "Email is required"}, status=400)

        # Find user
        user = UserRepository.find_by_email(email)
        if not user:
            return Response({"error": "User not found"}, status=404)

        if user.get("is_verified"):
            return Response({"message": "Account already verified"}, status=400)

        # Generate new code
        new_code = str(random.randint(100000, 999999))

        # Save it
        UserRepository.update_user(email, {"$set": {"verification_code": new_code}})

        # Send email
        try:
            send_mail(
                subject="Your New Verification Code",
                message=f"Your new verification code is {new_code}.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
        except Exception as e:
            return Response({"error": f"Failed to send email: {str(e)}"}, status=500)

        return Response({"message": "New verification code sent to your email"}, status=200)


# ---------------- Login ----------------
class LoginView(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        user = users.find_one({"email": email})
        if not user or not check_password(password, user["password"]):
            return Response({"error": "Invalid credentials"}, status=400)

        if not user.get("is_verified"):
            return Response({"error": "Account not verified"}, status=403)

        token = generate_jwt(user["_id"], user["email"])
        return Response({"token": token})


# ---------------- Profile ----------------
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "message": "This is a protected route",
            "user": request.user  # user comes from JWT payload
        })
