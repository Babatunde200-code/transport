import certifi
from pymongo import MongoClient
from django.conf import settings

def get_db():
    client = MongoClient(settings.MONGO_URI, tlsCAFile=certifi.where())
    return client["transport_db"]
