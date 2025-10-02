import jwt
import datetime
from django.conf import settings
from .models import User  # so we can fetch user by ID

# Secret key for signing JWT
JWT_SECRET = getattr(settings, "SECRET_KEY", "super-secret")
JWT_ALGORITHM = "HS256"
JWT_EXP_DELTA_SECONDS = 3600  # 1 hour


def generate_jwt(user):
    """Generate JWT token for a user"""
    payload = {
        "user_id": str(user.id),
        "email": user.email,
        "is_admin": user.is_admin,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=JWT_EXP_DELTA_SECONDS),
        "iat": datetime.datetime.utcnow(),
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token


def decode_jwt(token):
    """Decode JWT token and return payload if valid"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None  # token expired
    except jwt.InvalidTokenError:
        return None  # invalid


def get_user_from_token(request):
    """Extract user object from Authorization header JWT"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None

    token = auth_header.split(" ")[1]
    payload = decode_jwt(token)
    if not payload:
        return None

    # Look up user in DB
    user = User.find_by_id(payload.get("user_id"))
    return user
