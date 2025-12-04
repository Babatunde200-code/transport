import random
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.hashers import check_password as dj_check_password
from bson import ObjectId

from .repository import UserRepository
from .utils import generate_jwt
from .serializers import SignupSerializer
from travels.repositories import AdminRepository


# ---------------- Signup ----------------
class SignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        data = serializer.validated_data
        email = data["email"]
        password = data["password"]

        if UserRepository.find_by_email(email):
            return Response({"error": "Email already exists"}, status=400)

        verification_code = str(random.randint(100000, 999999))

        UserRepository.create_user({
            "email": email,
            "password": make_password(password),
            "is_verified": False,
            "verification_code": verification_code,
        })

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

        return Response(
            {
                "message": "Signup successful. Please check your email for the verification code.",
                "email": email
            },
            status=201,
        )


# ---------------- Verify Account ----------------
class VerifyAccountView(APIView):
    permission_classes = [AllowAny]

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
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"error": "Email is required"}, status=400)

        user = UserRepository.find_by_email(email)
        if not user:
            return Response({"error": "User not found"}, status=404)

        if user.get("is_verified"):
            return Response({"message": "Account already verified"}, status=400)

        new_code = str(random.randint(100000, 999999))
        UserRepository.update_user(email, {"$set": {"verification_code": new_code}})

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
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response({"error": "Email and password required"}, status=400)

        user = UserRepository.find_by_email(email)
        if not user:
            return Response({"error": "Invalid credentials"}, status=400)

        stored_password = user["password"]

        # Check password
        if dj_check_password(password, stored_password):
            pass
        elif password == stored_password:  # fallback old plain text
            UserRepository.update_password(user["_id"], make_password(password))
        else:
            return Response({"error": "Invalid credentials"}, status=400)

        # Check verification
        if not user.get("is_verified", False):
            return Response({"error": "Account not verified"}, status=403)

        # Admin role
        is_admin = user.get("is_admin", False)

        # Generate JWT
        token = generate_jwt(
            str(user["_id"]),
            user["email"],
            is_admin=is_admin,
        )

        return Response(
            {
                "message": "Login successful",
                "token": token,
                "email": user["email"],
                "is_admin": is_admin,
            },
            status=200,
        )


# ---------------- Forgot Password ----------------
class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")

        if not email:
            return Response({"error": "Email is required"}, status=400)

        user = UserRepository.find_by_email(email)
        if not user:
            return Response({"error": "User not found"}, status=404)

        reset_code = str(random.randint(100000, 999999))

        UserRepository.update_user(email, {"$set": {"reset_code": reset_code}})

        try:
            send_mail(
                subject="Password Reset Code",
                message=f"Your password reset code is {reset_code}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
        except Exception as e:
            return Response({"error": f"Email sending failed: {str(e)}"}, status=500)

        return Response({"message": "Password reset code sent to your email"}, status=200)


# ---------------- Reset Password ----------------
class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        code = request.data.get("code")
        new_password = request.data.get("new_password")

        if not email or not code or not new_password:
            return Response({"error": "Email, code, and new password are required"}, status=400)

        user = UserRepository.find_by_email(email)
        if not user:
            return Response({"error": "User not found"}, status=404)

        if user.get("reset_code") != code:
            return Response({"error": "Invalid reset code"}, status=400)

        hashed_password = make_password(new_password)

        UserRepository.update_user(
            email,
            {
                "$set": {"password": hashed_password},
                "$unset": {"reset_code": ""},  # remove used code
            },
        )

        return Response({"message": "Password reset successful"}, status=200)


# ---------------- Make Admin ----------------
class MakeAdminView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        email = request.data.get("email")

        if not email:
            return Response({"error": "Email is required"}, status=400)

        user = UserRepository.find_by_email(email)
        if not user:
            return Response({"error": "User not found"}, status=404)

        UserRepository.update_user(email, {"$set": {"is_admin": True}})

        return Response({"message": f"{email} promoted to admin"}, status=200)


# ---------------- Profile ----------------
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(
            {
                "message": "This is a protected route",
                "user": request.user,
            }
        )
