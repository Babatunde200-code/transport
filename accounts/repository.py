import certifi
from pymongo import MongoClient
from django.conf import settings

client = MongoClient(settings.MONGO_URI, tlsCAFile=certifi.where())
db = client[settings.MONGO_DB_NAME]
users_collection = db["users"]

class UserRepository:
    @staticmethod
    def find_by_email(email: str):
        return users_collection.find_one({"email": email})

    @staticmethod
    def create_user(data: dict):
        # ✅ Only keep allowed fields
        allowed_fields = {"email", "password", "is_verified", "verification_code"}
        clean_data = {k: v for k, v in data.items() if k in allowed_fields}

        users_collection.insert_one(clean_data)
        return clean_data
