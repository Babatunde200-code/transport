# accounts/models.py

from travelshare.mongo import get_db

db = get_db()
users_collection = db["users"] 

class UserRepository:
    collection = db["users"]

    @staticmethod
    def create_user(data):
        return UserRepository.collection.insert_one(data)

    @staticmethod
    def find_by_email(email):
        return UserRepository.collection.find_one({"email": email})

    @staticmethod
    def verify_user(email, code):
        return UserRepository.collection.update_one(
            {"email": email, "verification_code": code},
            {"$set": {"is_verified": True}}
        )

    @staticmethod
    def update_password(email, new_password):
        return UserRepository.collection.update_one(
            {"email": email},
            {"$set": {"password": new_password}}
        )
