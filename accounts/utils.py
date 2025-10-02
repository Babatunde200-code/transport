import jwt
from datetime import datetime, timedelta
from django.conf import settings

def generate_jwt(user_id, email, is_admin=False):
    role = "admin" if is_admin else "user"
    payload = {
        "user_id": str(user_id),
        "email": email,
        "role": role,
        "exp": datetime.utcnow() + timedelta(hours=2),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
