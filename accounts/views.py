import random
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import AllowAny,IsAuthenticated, IsAdminUser
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.hashers import check_password as dj_check_password
from bson import ObjectId
from .repository import UserRepository
from .utils import generate_jwt 
from .serializers import SignupSerializer
from .repository import UserRepository
from travels.utils import generate_jwt
from travels.repositories import AdminRepository   # ✅ now this works
from rest_framework.permissions import IsAdminUser

# ---------------- Signup ----------------
class SignupView(APIView):
    permission_classes = [AllowAny]  # ✅ anyone can sign up

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

        return Response({
            "message": "Signup successful. Please check your email for the verification code.",
            "email": email
        }, status=201)


# ---------------- Verify Account ----------------
class VerifyAccountView(APIView):
    permission_classes = [AllowAny]  # ✅ user not logged in yet

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
    permission_classes = [AllowAny]  # ✅ also public

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

        # 🔍 Look up user by email
        user = UserRepository.find_by_email(email)
        if not user:
            return Response({"error": "Invalid credentials"}, status=400)

        stored_password = user["password"]

        # ✅ Check password
        if dj_check_password(password, stored_password):
            pass  # correct password
        elif password == stored_password:  # fallback for old plain-text
            UserRepository.update_password(user["_id"], make_password(password))
        else:
            return Response({"error": "Invalid credentials"}, status=400)

        # 🚨 Block login if not verified
        if not user.get("is_verified", False):
            return Response({"error": "Account not verified"}, status=403)

        # 👮 Detect admin role
        is_admin = user.get("is_admin", False)

        # 🎫 Issue JWT
        token = generate_jwt(
            str(user["_id"]),
            user["email"],
            is_admin=is_admin
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
class MakeAdminView(APIView):
    permission_classes = [IsAdminUser]  # ✅ only admins can promote others

    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"error": "Email is required"}, status=400)

        # Find user
        user = UserRepository.find_by_email(email)
        if not user:
            return Response({"error": "User not found"}, status=404)

        # Update user to admin
        UserRepository.update_user(email, {"$set": {"is_admin": True}})

        return Response({"message": f"{email} promoted to admin"}, status=200)


# ---------------- Profile ----------------
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "message": "This is a protected route",
            "user": request.user  # user comes from JWT payload
        })
