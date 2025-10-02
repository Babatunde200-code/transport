# travels/auth_backend.py
from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
import jwt
from django.conf import settings


class JWTUser:
    def __init__(self, payload):
        self.id = payload.get("user_id")
        self.email = payload.get("email")
        self.role = payload.get("role", "user")
        self.is_staff = payload.get("is_staff", False)
        self.is_authenticated = True  # ✅ DRF expects this


class PyMongoJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None

        token = auth_header.split(" ")[1]

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed("Token expired")
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed("Invalid token")

        user = JWTUser(payload)  # ✅ wrap in class, not dict
        return (user, None)
