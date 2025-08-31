import random
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import UserRepository
from .utils import SignupSerializer
from rest_framework import status, permissions
from bson.objectid import ObjectId
from rest_framework.permissions import IsAuthenticated
from .auth_utils import users, hash_password, check_password, generate_jwt


class SignupView(APIView):
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        data = serializer.validated_data
        if UserRepository.find_by_email(data["email"]):
            return Response({"error": "Email already exists"}, status=400)

        verification_code = str(random.randint(100000, 999999))

        UserRepository.create_user({
            "full_name": data["full_name"],
            "email": data["email"],
            "phone_number": data["phone_number"],
            "password": data["password"],  # TODO: hash before saving
            "is_verified": False,
            "verification_code": verification_code
        })

        return Response({"message": "Signup successful. Please verify your account."})


class VerifyAccountView(APIView):
    def post(self, request):
        email = request.data.get("email")
        code = request.data.get("code")

        result = UserRepository.verify_user(email, code)
        if result.modified_count == 0:
            return Response({"error": "Invalid code or email"}, status=400)

        return Response({"message": "Account verified successfully"})




class RegisterView(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if users.find_one({"email": email}):
            return Response({"error": "Email already registered"}, status=400)

        hashed = hash_password(password)
        user = {
            "email": email,
            "password": hashed,
            "is_active": True
        }
        result = users.insert_one(user)
        return Response({"message": "User created", "id": str(result.inserted_id)})


class LoginView(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        user = users.find_one({"email": email})
        if not user or not check_password(password, user["password"]):
            return Response({"error": "Invalid credentials"}, status=400)

        token = generate_jwt(user["_id"], user["email"])
        return Response({"token": token})


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "message": "This is a protected route",
            "user": request.user  # user comes from JWT payload
        })
