# travels/db.py
import certifi
from pymongo import MongoClient
from django.conf import settings

_client = None
_db = None

def get_db():
    global _client, _db
    if _db is None:
        _client = MongoClient(settings.MONGO_URI, tlsCAFile=certifi.where(), serverSelectionTimeoutMS=5000)
        _db = _client[settings.MONGO_DB_NAME]
    return _db

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

# Define all collections in one place, resolved lazily
users_collection = LazyCollection("users")
admins_collection = LazyCollection("admins")
trips_collection = LazyCollection("trips")
bookings_collection = LazyCollection("bookings")
rides_collection = LazyCollection("rides")
payments_collection = LazyCollection("payments")
db = LazyCollection("dummy")