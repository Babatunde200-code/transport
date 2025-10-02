import jwt
from django.conf import settings
from datetime import datetime, timedelta


def generate_jwt(user_id, email, is_admin=False):
    """
    Generate JWT token for users or admins.
    """
    role = "admin" if is_admin else "user"
    payload = {
        "user_id": str(user_id),
        "email": email,
        "role": role,
        "is_staff": is_admin,   # ✅ useful for IsAdminUser
        "exp": datetime.utcnow() + timedelta(hours=2),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
