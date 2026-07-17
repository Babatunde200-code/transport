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

    @staticmethod
    def verify_user(email: str, code: str):
        """
        Marks a user as verified if the email + code match
        """
        return users_collection.update_one(
            {
                "email": email,
                "verification_code": code,
                "is_verified": False,  # only verify if not already verified
            },
            {
                "$set": {"is_verified": True},
                "$unset": {"verification_code": ""},  # remove code after success
            }
        )

    @staticmethod
    def update_user(email: str, update_dict: dict):
        """
        Updates a user document matched by email.
        """
        return users_collection.update_one({"email": email}, update_dict)

    @staticmethod
    def update_password(user_id, hashed_password: str):
        """
        Updates a user's password matched by user_id.
        """
        from bson import ObjectId
        return users_collection.update_one(
            {"_id": ObjectId(user_id) if isinstance(user_id, str) else user_id},
            {"$set": {"password": hashed_password}}
        )
