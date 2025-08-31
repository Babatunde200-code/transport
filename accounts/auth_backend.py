import jwt
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from bson.objectid import ObjectId
from .auth_utils import users

class PyMongoJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            return None  # No auth provided

        token = auth_header.split(" ")[1]

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Token expired")
        except jwt.InvalidTokenError:
            raise AuthenticationFailed("Invalid token")

        user = users.find_one({"_id": ObjectId(payload["user_id"])})
        if not user:
            raise AuthenticationFailed("User not found")

        # Minimal user object (since we’re not using Django ORM User model)
        request.user = {
            "id": str(user["_id"]),
            "email": user["email"],
        }

        return (request.user, None)
