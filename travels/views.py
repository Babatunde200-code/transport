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
from .utils import generate_jwt

SECRET_KEY = settings.SECRET_KEY


# -------------------------------------------------
# SAFE OBJECT ID
# -------------------------------------------------
def _safe_object_id(val):
    if not val:
        return None
    try:
        return ObjectId(val)
    except:
        return val


# -------------------------------------------------
# ADMIN SIGNUP
# -------------------------------------------------
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


# -------------------------------------------------
# ADMIN LOGIN
# -------------------------------------------------
class AdminLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        admin = AdminRepository.find_by_email(email)
        if not admin:
            return Response({"error": "Invalid credentials"}, status=401)

        stored_password = admin.get("password", "")

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


# -------------------------------------------------
# ADMIN RIDE CRUD
# -------------------------------------------------
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


# -------------------------------------------------
# LIST RIDES
# -------------------------------------------------
class RideListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        rides = list(trips_collection.find({}))

        for r in rides:
            r["_id"] = str(r["_id"])

        return Response(rides, status=200)


# -------------------------------------------------
# BOOK A RIDE
# -------------------------------------------------
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
            "user": str(user_id),
            "email": email,
            "seat_number": seat_number,
            "amount": int(ride["price"]),
            "payment_status": "unpaid",
            "created_at": datetime.utcnow()
        }

        result = bookings_collection.insert_one(booking)

        trips_collection.update_one(
            {"_id": ride["_id"]},
            {
                "$push": {"booked_seats": seat_number},
                "$inc": {"available_seats": -1}
            }
        )

        booking["_id"] = str(result.inserted_id)

        return Response(booking, status=201)


# -------------------------------------------------
# USER BOOKINGS LIST
# -------------------------------------------------
class UserBookingsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = str(payload["user_id"])

        bookings = list(bookings_collection.find({"user": user_id}))

        for b in bookings:
            b["_id"] = str(b["_id"])

        return Response(bookings, status=200)


# -------------------------------------------------
# BOOKING DETAIL
# -------------------------------------------------
class BookingDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, booking_id):
        booking = bookings_collection.find_one({"_id": _safe_object_id(booking_id)})
        if not booking:
            return Response({"error": "Booking not found"}, status=404)

        booking["_id"] = str(booking["_id"])
        return Response(booking, status=200)


# -------------------------------------------------
# MARK BOOKING AS PAID
# -------------------------------------------------
class MarkPaidView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, booking_id):
        booking = bookings_collection.find_one({"_id": _safe_object_id(booking_id)})
        if not booking:
            return Response({"error": "Booking not found"}, status=404)

        bookings_collection.update_one(
            {"_id": booking["_id"]},
            {"$set": {"payment_status": "paid"}}
        )

        return Response({"message": "Payment marked as paid"}, status=200)


# -------------------------------------------------
# DASHBOARD — RECENT BOOKINGS
# -------------------------------------------------
class DashboardBookingsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = str(payload["user_id"])

        bookings = list(
            bookings_collection.find({"user": user_id})
            .sort("created_at", -1)  
            .limit(5)
        )

        for b in bookings:
            b["_id"] = str(b["_id"])

        return Response({"recent_bookings": bookings}, status=200)


# -------------------------------------------------
# DASHBOARD — TOTAL PAYMENTS
# -------------------------------------------------
class DashboardPaymentsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = str(payload["user_id"])

        payments = list(payments_collection.find({"user_id": user_id}))

        total = sum(float(p.get("amount", 0)) for p in payments)

        return Response({"total_payments": total}, status=200)


# -------------------------------------------------
# DASHBOARD — PENDING PAYMENTS
# -------------------------------------------------
class DashboardPendingPaymentsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = str(payload["user_id"])

        pending = bookings_collection.count_documents({
            "user": user_id,
            "payment_status": {"$ne": "paid"}
        })

        return Response({"pending_payments": pending}, status=200)


# -------------------------------------------------
# PAYMENT WEBHOOK (FLUTTERWAVE)
# -------------------------------------------------
@api_view(["POST"])
def verify_payment(request):
    data = request.data
    booking_id = data.get("booking_id")
    amount = float(data.get("amount", 0))
    user_id = data.get("user_id")

    booking = bookings_collection.find_one({"_id": _safe_object_id(booking_id)})
    if booking and not user_id:
        user_id = booking.get("user")

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
        {"$set": {"payment_status": "paid"}}
    )

    return Response({"message": "Payment verified"}, status=200)

