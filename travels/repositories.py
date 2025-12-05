from bson import ObjectId
from .db import admins_collection 
from .db import payments_collection
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
class PaymentRepository:
    
    @staticmethod
    def find_by_user(user_id):
        return list(payments_collection.find({"user_id": user_id}))

    @staticmethod
    def find_pending(user_id):
        return list(payments_collection.find({"user_id": user_id, "status": "pending"}))

    @staticmethod
    def create(payment):
        return payments_collection.insert_one(payment)

    @staticmethod
    def all():
        return list(payments_collection.find({}))