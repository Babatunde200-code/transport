from bson import ObjectId
from django.contrib.auth.hashers import make_password, check_password
from datetime import datetime
from .db import users_collection, rides_collection, bookings_collection, payments_collection

# MongoDB collections
users = users_collection
rides = rides_collection
bookings = bookings_collection


# ===================== USER =====================
class User:
    def __init__(self, email, password=None, is_admin=False, _id=None, created_at=None):
        self.id = str(_id) if _id else None
        self.email = email
        self.password = password
        self.is_admin = is_admin
        self.created_at = created_at or datetime.utcnow()

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def save(self):
        doc = {
            "email": self.email,
            "password": self.password,
            "is_admin": self.is_admin,
            "created_at": self.created_at,
        }
        if self.id:
            users.update_one({"_id": ObjectId(self.id)}, {"$set": doc})
        else:
            result = users.insert_one(doc)
            self.id = str(result.inserted_id)
        return self

    @staticmethod
    def find_by_email(email: str):
        data = users.find_one({"email": email})
        if not data:
            return None
        return User(
            email=data["email"],
            password=data["password"],
            is_admin=data.get("is_admin", False),
            _id=data["_id"],
            created_at=data.get("created_at"),
        )

    @staticmethod
    def find_by_id(user_id: str):
        try:
            data = users.find_one({"_id": ObjectId(user_id)})
        except Exception:
            return None
        if not data:
            return None
        return User(
            email=data["email"],
            password=data["password"],
            is_admin=data.get("is_admin", False),
            _id=data["_id"],
            created_at=data.get("created_at"),
        )

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "is_admin": self.is_admin,
            "created_at": self.created_at,
        }


# ===================== RIDE =====================
class Ride:
    def __init__(
        self,
        origin,
        destination,
        departure_time,
        price,
        available_seats,
        total_seats=None,
        booked_seats=None,
        _id=None
    ):
        self.id = str(_id) if _id else None
        self.origin = origin
        self.destination = destination
        self.departure_time = departure_time
        self.price = price
        self.available_seats = available_seats

        # New fields
        self.total_seats = total_seats or available_seats
        self.booked_seats = booked_seats or []

    def save(self):
        doc = {
            "origin": self.origin,
            "destination": self.destination,
            "departure_time": self.departure_time,
            "price": self.price,
            "available_seats": self.available_seats,

            # ✔ MUST BE INCLUDED
            "total_seats": self.total_seats,
            "booked_seats": self.booked_seats,
        }

        if self.id:
            rides.update_one({"_id": ObjectId(self.id)}, {"$set": doc})
        else:
            result = rides.insert_one(doc)
            self.id = str(result.inserted_id)

        return self

    @staticmethod
    def find_all():
        return [
            Ride(
                origin=r["origin"],
                destination=r["destination"],
                departure_time=r["departure_time"],
                price=r["price"],
                available_seats=r["available_seats"],
                total_seats=r.get("total_seats", r["available_seats"]),
                booked_seats=r.get("booked_seats", []),
                _id=r["_id"],
            )
            for r in rides.find()
        ]

    @staticmethod
    def find_by_id(ride_id):
        try:
            r = rides.find_one({"_id": ObjectId(ride_id)})
        except Exception:
            return None
        if not r:
            return None
        return Ride(
            origin=r["origin"],
            destination=r["destination"],
            departure_time=r["departure_time"],
            price=r["price"],
            available_seats=r["available_seats"],
            total_seats=r.get("total_seats", r["available_seats"]),
            booked_seats=r.get("booked_seats", []),
            _id=r["_id"],
        )


# ===================== BOOKING =====================
class Booking:
    def __init__(self, user_id, ride_id, seat_count, total_price, status="pending", _id=None, created_at=None):
        self.id = str(_id) if _id else None
        self.user_id = user_id
        self.ride_id = ride_id
        self.seat_count = seat_count
        self.total_price = total_price
        self.status = status
        self.created_at = created_at or datetime.utcnow()

    def save(self):
        doc = {
            "user_id": self.user_id,
            "ride_id": self.ride_id,
            "seat_count": self.seat_count,
            "total_price": self.total_price,
            "status": self.status,
            "created_at": self.created_at,
        }
        if self.id:
            bookings.update_one({"_id": ObjectId(self.id)}, {"$set": doc})
        else:
            result = bookings.insert_one(doc)
            self.id = str(result.inserted_id)
        return self

    @staticmethod
    def find_by_user(user_id):
        return [
            Booking(
                user_id=b["user_id"],
                ride_id=b["ride_id"],
                seat_count=b["seat_count"],
                total_price=b["total_price"],
                status=b["status"],
                _id=b["_id"],
                created_at=b["created_at"],
            )
            for b in bookings.find({"user_id": user_id})
        ]

    @staticmethod
    def find_by_id(booking_id):
        try:
            b = bookings.find_one({"_id": ObjectId(booking_id)})
        except Exception:
            return None
        if not b:
            return None
        return Booking(
            user_id=b["user_id"],
            ride_id=b["ride_id"],
            seat_count=b["seat_count"],
            total_price=b["total_price"],
            status=b["status"],
            _id=b["_id"],
            created_at=b["created_at"],
        )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "ride_id": self.ride_id,
            "seat_count": self.seat_count,
            "total_price": self.total_price,
            "status": self.status,
            "created_at": self.created_at,
        }

# ===================== PAYMENT =====================
payments = payments_collection

class Payment:
    def __init__(self, user_id, booking_id, amount, status="pending", created_at=None, _id=None):
        self.id = str(_id) if _id else None
        self.user_id = user_id
        self.booking_id = booking_id
        self.amount = amount
        self.status = status  # paid | pending
        self.created_at = created_at or datetime.utcnow()

    def save(self):
        doc = {
            "user_id": self.user_id,
            "booking_id": self.booking_id,
            "amount": self.amount,
            "status": self.status,
            "created_at": self.created_at,
        }
        if self.id:
            payments.update_one({"_id": ObjectId(self.id)}, {"$set": doc})
        else:
            result = payments.insert_one(doc)
            self.id = str(result.inserted_id)
        return self

    @staticmethod
    def find_by_user(user_id):
        return [
            Payment(
                user_id=p["user_id"],
                booking_id=p["booking_id"],
                amount=p["amount"],
                status=p["status"],
                created_at=p["created_at"],
                _id=p["_id"]
            )
            for p in payments.find({"user_id": user_id})
        ]

    @staticmethod
    def find_pending(user_id):
        return [
            Payment(
                user_id=p["user_id"],
                booking_id=p["booking_id"],
                amount=p["amount"],
                status=p["status"],
                created_at=p["created_at"],
                _id=p["_id"]
            )
            for p in payments.find({"user_id": user_id, "status": "pending"})
        ]

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "booking_id": self.booking_id,
            "amount": self.amount,
            "status": self.status,
            "created_at": self.created_at,
        }
