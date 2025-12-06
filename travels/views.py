# travel/views.py
import jwt
from django.conf import settings
from datetime import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from bson.objectid import ObjectId
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from django.contrib.auth.hashers import check_password as dj_check_password, make_password
from rest_framework.decorators import api_view

from .db import admins_collection, trips_collection, bookings_collection, payments_collection
from .repositories import AdminRepository
from .utils import generate_jwt, send_telegram_alert

SECRET_KEY = settings.SECRET_KEY


# ---------------- Helper ----------------
def _safe_object_id(val):
    if not val:
        return None
    try:
        return ObjectId(val)
    except:
        return val


# ------------------- ADMIN AUTH -------------------
class AdminSignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response({"error": "Email and password required"}, status=400)

        if admins_collection.find_one({"email": email}):
            return Response({"error": "Admin already exists"}, status=400)

        admins_collection.insert_one({
            "email": email,
            "password": make_password(password),
            "role": "admin",
            "created_at": datetime.utcnow()
        })

        return Response({"message": "Admin created"}, status=201)


class AdminLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        admin = AdminRepository.find_by_email(email)
        if not admin:
            return Response({"error": "Invalid credentials"}, status=401)

        stored_password = admin.get("password", "")

        # Handle migration from plaintext
        if dj_check_password(password, stored_password):
            pass
        elif password == stored_password:
            AdminRepository.update_password(admin["_id"], make_password(password))
        else:
            return Response({"error": "Invalid credentials"}, status=401)

        token = generate_jwt(str(admin["_id"]), admin["email"], is_admin=True)

        return Response({
            "token": token,
            "is_admin": True,
            "email": admin["email"]
        }, status=200)


# ------------------- ADMIN RIDE MANAGEMENT -------------------
class AdminRideView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        data = request.data

        total_seats = int(data.get("total_seats", 0))

        ride = {
            "origin": data.get("origin"),
            "destination": data.get("destination"),
            "departure_time": data.get("departure_time"),
            "total_seats": total_seats,
            "available_seats": total_seats,
            "booked_seats": [],
            "price": int(data.get("price", 0)),
            "created_at": datetime.utcnow()
        }

        result = trips_collection.insert_one(ride)
        ride["_id"] = str(result.inserted_id)

        return Response(ride, status=201)

    def put(self, request, ride_id):
        ride_doc = trips_collection.find_one({"_id": _safe_object_id(ride_id)})
        if not ride_doc:
            return Response({"error": "Ride not found"}, status=404)

        data = request.data
        total_seats = int(data.get("total_seats", ride_doc["total_seats"]))
        booked = ride_doc.get("booked_seats", [])
        available = max(total_seats - len(booked), 0)

        update = {
            "origin": data.get("origin", ride_doc["origin"]),
            "destination": data.get("destination", ride_doc["destination"]),
            "departure_time": data.get("departure_time", ride_doc["departure_time"]),
            "total_seats": total_seats,
            "available_seats": available,
            "price": int(data.get("price", ride_doc["price"])),
            "updated_at": datetime.utcnow()
        }

        trips_collection.update_one({"_id": ride_doc["_id"]}, {"$set": update})
        return Response({"message": "Ride updated"}, status=200)

    def delete(self, request, ride_id):
        result = trips_collection.delete_one({"_id": _safe_object_id(ride_id)})
        if result.deleted_count == 0:
            return Response({"error": "Ride not found"}, status=404)
        return Response({"message": "Ride deleted"}, status=200)


# ------------------- USER: LIST RIDES -------------------
class RideListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        rides = list(trips_collection.find({}, {
            "_id": 1,
            "origin": 1,
            "destination": 1,
            "departure_time": 1,
            "total_seats": 1,
            "available_seats": 1,
            "booked_seats": 1,
            "price": 1
        }))

        for r in rides:
            r["_id"] = str(r["_id"])

        return Response(rides, status=200)


# ------------------- BOOKINGS -------------------
class BookRideView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, ride_id):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

        user_id = payload["user_id"]
        email = payload["email"]

        seat_number = int(request.data.get("seat_number"))

        ride = trips_collection.find_one({"_id": _safe_object_id(ride_id)})
        if not ride:
            return Response({"error": "Ride not found"}, status=404)

        if seat_number in ride.get("booked_seats", []):
            return Response({"error": "Seat already taken"}, status=400)

        booking = {
            "ride_id": str(ride["_id"]),
            "user_id": user_id,
            "email": email,
            "seat_number": seat_number,
            "price": int(ride["price"]),
            "status": "pending",
            "created_at": datetime.utcnow()
        }

        result = bookings_collection.insert_one(booking)

        # Update ride seats
        trips_collection.update_one(
            {"_id": ride["_id"]},
            {
                "$push": {"booked_seats": seat_number},
                "$inc": {"available_seats": -1}
            }
        )

        booking["_id"] = str(result.inserted_id)

        return Response(booking, status=201)


# ------------------- USER BOOKINGS -------------------
class UserBookingsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload["user_id"]

        bookings = list(bookings_collection.find({"user_id": user_id}))

        output = []
        for b in bookings:
            ride = trips_collection.find_one({"_id": _safe_object_id(b["ride_id"])})
            output.append({
                "booking_id": str(b["_id"]),
                "seat_number": b["seat_number"],
                "status": b["status"],
                "total_price": b.get("price", 0),
                "ride": {
                    "origin": ride["origin"],
                    "destination": ride["destination"],
                    "departure_time": ride["departure_time"]
                } if ride else None
            })

        return Response(output, status=200)


# ------------------- DASHBOARD SUMMARY -------------------
class DashboardSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload["user_id"]

        total_trips = bookings_collection.count_documents({"user_id": user_id})

        total_payments = sum([
            float(p.get("amount", 0))
            for p in payments_collection.find({"user_id": user_id, "status": "paid"})
        ])

        pending = payments_collection.count_documents({
            "user_id": user_id,
            "status": {"$in": ["pending", "unpaid"]}
        })

        return Response({
            "total_trips": total_trips,
            "total_payments": total_payments,
            "pending_payments": pending,
            "travel_history_count": total_trips
        })


# ------------------- PAYMENT WEBHOOK -------------------
@api_view(["POST"])
def verify_payment(request):
    data = request.data
    booking_id = data.get("booking_id")
    amount = float(data.get("amount", 0))
    user_id = data.get("user_id")

    booking = bookings_collection.find_one({"_id": _safe_object_id(booking_id)})
    if booking and not user_id:
        user_id = booking.get("user_id")

    payments_collection.insert_one({
        "booking_id": booking_id,
        "user_id": user_id,
        "amount": amount,
        "status": "paid",
        "transaction_id": data.get("transaction_id"),
        "created_at": datetime.utcnow()
    })

    bookings_collection.update_one(
        {"_id": _safe_object_id(booking_id)},
        {"$set": {"status": "paid"}}
    )

    return Response({"message": "Payment verified"}, status=200)
