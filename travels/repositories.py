from bson import ObjectId
from .db import admins_collection   # adjust import if your db connection is elsewhere
from django.contrib.auth.hashers import make_password


class AdminRepository:
    @staticmethod
    def find_by_email(email):
        return admins_collection.find_one({"email": email})

    @staticmethod
    def update_password(admin_id, new_password):
        admins_collection.update_one(
            {"_id": ObjectId(admin_id)},
            {"$set": {"password": make_password(new_password)}}
        )
