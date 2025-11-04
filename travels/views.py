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
from .db import admins_collection, trips_collection, bookings_collection
from .repositories import AdminRepository
from .utils import generate_jwt
from .serializers import BookingSerializer

from rest_framework.decorators import api_view
from rest_framework.response import Response
from .utils import send_telegram_alert

SECRET_KEY = settings.SECRET_KEY


# ------------------- ADMIN -------------------
class AdminSignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if admins_collection.find_one({"email": email}):
            return Response({"error": "Admin already exists"}, status=400)

        new_admin = {
            "email": email,
            "password": make_password(password),
            "role": "admin",
            "created_at": datetime.utcnow()
        }
        admins_collection.insert_one(new_admin)
        return Response({"message": "Admin created"}, status=201)


class AdminLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response({"error": "Email and password required"}, status=400)

        admin = AdminRepository.find_by_email(email)
        if not admin:
            return Response({"error": "Invalid credentials"}, status=401)

        stored_password = admin["password"]

        if dj_check_password(password, stored_password):
            pass
        elif password == stored_password:  # fallback for old plaintext
            AdminRepository.update_password(admin["_id"], make_password(password))
        else:
            return Response({"error": "Invalid credentials"}, status=401)

        token = generate_jwt(
            str(admin["_id"]),
            admin["email"],
            is_admin=True
        )

        return Response(
            {"token": token, "is_admin": True, "email": admin["email"]},
            status=200
        )


class AdminRideView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        """Admin creates ride"""
        data = request.data
        ride = {
            "origin": data.get("origin"),
            "destination": data.get("destination"),
            "departure_time": data.get("departure_time"),
            "available_seats": int(data.get("available_seats", 0)),
            "price": int(data.get("price", 0)),
            "created_at": datetime.utcnow()
        }
        result = trips_collection.insert_one(ride)
        ride["_id"] = str(result.inserted_id)
        return Response(ride, status=201)

    def put(self, request, ride_id):
        """Admin updates ride"""
        data = request.data
        update_data = {
            "origin": data.get("origin"),
            "destination": data.get("destination"),
            "departure_time": data.get("departure_time"),
            "available_seats": int(data.get("available_seats", 0)),
            "price": int(data.get("price", 0)),
            "updated_at": datetime.utcnow()
        }
        result = trips_collection.update_one(
            {"_id": ObjectId(ride_id)},
            {"$set": update_data}
        )
        if result.matched_count == 0:
            return Response({"error": "Ride not found"}, status=404)
        return Response({"message": "Ride updated"}, status=200)

    def delete(self, request, ride_id):
        result = trips_collection.delete_one({"_id": ObjectId(ride_id)})
        if result.deleted_count == 0:
            return Response({"error": "Ride not found"}, status=404)
        return Response({"message": "Ride deleted"}, status=200)


# ------------------- USER RIDES -------------------
class RideListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        rides = list(trips_collection.find({}, {
            "_id": 1,
            "origin": 1,
            "destination": 1,
            "departure_time": 1,
            "available_seats": 1,
            "price": 1
        }))
        for ride in rides:
            ride["_id"] = str(ride["_id"])
        return Response(rides, status=200)


# ------------------- BOOKINGS -------------------
class BookRideView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, ride_id):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return Response({"error": "Token expired"}, status=401)
        except jwt.InvalidTokenError:
            return Response({"error": "Invalid token"}, status=401)

        user_id = payload.get("user_id")
        email = payload.get("email")

        seat_count = int(request.data.get("seat_count", 1))

        ride = trips_collection.find_one({"_id": ObjectId(ride_id)})
        if not ride:
            return Response({"error": "Ride not found"}, status=404)

        available_seats = ride.get("available_seats", 0)
        if available_seats < seat_count:
            return Response({"error": f"Only {available_seats} seat(s) left"}, status=400)

        booking = {
            "ride_id": str(ride["_id"]),
            "user_id": user_id,
            "email": email,
            "seat_count": seat_count,
            "total_price": seat_count * int(ride["price"]),
            "status": "pending",
            "created_at": datetime.utcnow()
        }
        result = bookings_collection.insert_one(booking)
        booking["_id"] = str(result.inserted_id)

        trips_collection.update_one(
            {"_id": ride["_id"]},
            {"$inc": {"available_seats": -seat_count}}
        )

        return Response(booking, status=201)


class UserBookingsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except jwt.InvalidTokenError:
            return Response({"error": "Unauthorized"}, status=401)

        user_id = payload.get("user_id")
        bookings = list(bookings_collection.find({"user_id": user_id}))
        for b in bookings:
            b["_id"] = str(b["_id"])
        return Response(bookings, status=200)
    
class BookingDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, booking_id):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except jwt.InvalidTokenError:
            return Response({"error": "Unauthorized"}, status=401)

        user_id = payload.get("user_id")

        booking = bookings_collection.find_one(
            {"_id": ObjectId(booking_id), "user_id": user_id}
        )
        if not booking:
            return Response({"error": "Booking not found"}, status=404)

        ride = trips_collection.find_one({"_id": ObjectId(booking["ride_id"])})
        if ride:
            booking["ride"] = {
                "origin": ride.get("origin"),
                "destination": ride.get("destination"),
                "departure_time": ride.get("departure_time"),
                "price": ride.get("price")
            }

        booking["_id"] = str(booking["_id"])
        return Response(booking, status=200)


class MarkPaidView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, booking_id):
        result = bookings_collection.update_one(
            {"_id": ObjectId(booking_id)},
            {"$set": {"status": "paid"}}
        )
        if result.matched_count == 0:
            return Response({"error": "Booking not found"}, status=404)
        return Response({"message": "Payment confirmed", "status": "paid"})



@api_view(["POST"])
def verify_payment(request):
    data = request.data
    transaction_id = data.get("transaction_id")
    booking_id = data.get("booking_id")
    amount = data.get("amount")
    name = data.get("name")
    email = data.get("email")

    message = f"""
💳 <b>New Payment Received!</b>
👤 <b>Name:</b> {name}
📧 <b>Email:</b> {email}
📦 <b>Booking ID:</b> {booking_id}
💰 <b>Amount:</b> ₦{amount}
🧾 <b>Transaction ID:</b> {transaction_id}
    """
    send_telegram_alert(message)

    return Response({"message": "Payment verified and alert sent."}, status=200)
