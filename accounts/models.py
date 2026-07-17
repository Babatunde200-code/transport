# accounts/models.py
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

users_collection = LazyCollection("users")

class UserRepository:
    collection = users_collection

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
