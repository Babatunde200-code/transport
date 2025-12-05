# travels/db.py
from pymongo import MongoClient
from django.conf import settings

# Connect to MongoDB
client = MongoClient(settings.MONGO_URI)
db = client[settings.MONGO_DB_NAME]

# Define all collections in one place
users_collection = db["users"]
admins_collection = db["admins"]
trips_collection = db["trips"]
bookings_collection = db["bookings"]
rides_collection = db["rides"]
payments_collection = db["payments"]