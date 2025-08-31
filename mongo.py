import certifi
from pymongo import MongoClient
from django.conf import settings

_client = None
_db = None

def get_db():
    """
    Lazily initializes and returns a MongoDB connection.
    """
    global _client, _db
    if _db is None:
        _client = MongoClient(settings.MONGO_URI, tlsCAFile=certifi.where())
        _db = _client["transport_db"]
    return _db
