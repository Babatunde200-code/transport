import jwt
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from bson.objectid import ObjectId
from .auth_utils import users
from travels.db import admins_collection   # ✅ import correctly


class MongoUser:
    def __init__(self, user_id, email, role, is_staff=False):
        self.id = user_id
        self.email = email
        self.role = role
        self.is_staff = is_staff

    @property
    def is_authenticated(self):
        return True   # ✅ Always true if token is valid


class PyMongoJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            return None

        token = auth_header.split(" ")[1]

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Token expired")
        except jwt.InvalidTokenError:
            raise AuthenticationFailed("Invalid token")

        user = None
        role = payload.get("role")

        if role == "user":
            user = users.find_one({"_id": ObjectId(payload["user_id"])})
            is_staff = False
        elif role == "admin":
            user = admins_collection.find_one({"_id": ObjectId(payload["user_id"])})
            is_staff = True
        else:
            raise AuthenticationFailed("Invalid role in token")

        if not user:
            raise AuthenticationFailed("User not found")

        # ✅ Wrap in MongoUser instead of dict
        mongo_user = MongoUser(
            user_id=str(user["_id"]),
            email=user["email"],
            role=role,
            is_staff=is_staff,
        )

        return (mongo_user, None)
