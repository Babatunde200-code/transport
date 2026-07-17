import bcrypt
import jwt
import datetime
from django.conf import settings
from bson.objectid import ObjectId
from travelshare.mongo import get_db

class LazyCollection:
    def __init__(self, collection_name):
        self._collection_name = collection_name
        self._collection = None

    def _resolve(self):
        if self._collection is None:
            self._collection = get_db()[self._collection_name]
        return self._collection

    def __getattr__(self, name):
        return getattr(self._resolve(), name)

    def __getitem__(self, key):
        return self._resolve()[key]

users = LazyCollection("users")

# password helpers
def hash_password(password: str) -> bytes:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def check_password(password: str, hashed: bytes) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed)

# JWT helpers
def generate_jwt(user_id: str, email: str):
    payload = {
        "user_id": str(user_id),
        "email": email,
        "role": "user",  # default to user
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24),
        "iat": datetime.datetime.utcnow()
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    return token
