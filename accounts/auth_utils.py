import bcrypt
import jwt
import datetime
from django.conf import settings
from bson.objectid import ObjectId

from pymongo import MongoClient

# connect to MongoDB
client = MongoClient(settings.MONGO_URI)
db = client[settings.MONGO_DB_NAME]
users = db["users"]   # or "accounts_customeruser"

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
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24),
        "iat": datetime.datetime.utcnow()
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    return token
