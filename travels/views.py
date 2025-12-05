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
from .db import admins_collection, trips_collection, bookings_collection
from .repositories import AdminRepository
from .utils import generate_jwt, send_telegram_alert
from .db import payments_collection

SECRET_KEY = settings.SECRET_KEY


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

        stored_password = admin.get("password", "")

        if dj_check_password(password, stored_password):
            pass
        elif password == stored_password:  # fallback for plaintext migration
            AdminRepository.update_password(admin["_id"], make_password(password))
        else:
            return Response({"error": "Invalid credentials"}, status=401)

        token = generate_jwt(str(admin["_id"]), admin["email"], is_admin=True)
        return Response({"token": token, "is_admin": True, "email": admin["email"]}, status=200)


# ------------------- ADMIN RIDE MANAGEMENT -------------------
class AdminRideView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        """Create a new ride (admin)."""
        data = request.data
        try:
            total_seats = int(data.get("total_seats", 0))
        except (TypeError, ValueError):
            total_seats = 0

        ride = {
            "origin": data.get("origin"),
            "destination": data.get("destination"),
            "departure_time": data.get("departure_time"),
            "total_seats": total_seats,
            "available_seats": total_seats,
            "booked_seats": [],
            "price": int(data.get("price", 0)) if data.get("price") is not None else 0,
            "created_at": datetime.utcnow()
        }

        result = trips_collection.insert_one(ride)
        ride["_id"] = str(result.inserted_id)
        return Response(ride, status=201)

    def put(self, request, ride_id):
        """Update existing ride (admin). Preserves booked_seats."""
        data = request.data

        ride = trips_collection.find_one({"_id": ObjectId(ride_id)})
        if not ride:
            return Response({"error": "Ride not found"}, status=404)

        try:
            total_seats = int(data.get("total_seats", ride.get("total_seats", 0)))
        except (TypeError, ValueError):
            total_seats = ride.get("total_seats", 0)

        booked = ride.get("booked_seats", [])
        # Recalculate available seats: ensure non-negative
        available = max(total_seats - len(booked), 0)

        update_data = {
            "origin": data.get("origin", ride.get("origin")),
            "destination": data.get("destination", ride.get("destination")),
            "departure_time": data.get("departure_time", ride.get("departure_time")),
            "total_seats": total_seats,
            "available_seats": available,
            "price": int(data.get("price", ride.get("price", 0))),
            "updated_at": datetime.utcnow()
        }

        trips_collection.update_one({"_id": ObjectId(ride_id)}, {"$set": update_data})
        return Response({"message": "Ride updated"}, status=200)

    def delete(self, request, ride_id):
        result = trips_collection.delete_one({"_id": ObjectId(ride_id)})
        if result.deleted_count == 0:
            return Response({"error": "Ride not found"}, status=404)
        return Response({"message": "Ride deleted"}, status=200)


# ------------------- USER: LIST RIDES -------------------
class RideListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        # Return rides with the fields frontend expects
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

        for ride in rides:
            ride["_id"] = str(ride["_id"])
            ride["booked_seats"] = ride.get("booked_seats", [])
        return Response(rides, status=200)


# ------------------- BOOKINGS -------------------
class BookRideView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, ride_id):
        # Authenticate token
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return Response({"error": "Token expired"}, status=401)
        except jwt.InvalidTokenError:
            return Response({"error": "Invalid token"}, status=401)

        user_id = payload.get("user_id")
        email = payload.get("email")

        # Validate seat_number
        seat_number = request.data.get("seat_number")
        if seat_number is None:
            return Response({"error": "Seat number is required"}, status=400)
        try:
            seat_number = int(seat_number)
        except (TypeError, ValueError):
            return Response({"error": "Seat number must be an integer"}, status=400)

        # Load ride
        ride = trips_collection.find_one({"_id": ObjectId(ride_id)})
        if not ride:
            return Response({"error": "Ride not found"}, status=404)

        total_seats = ride.get("total_seats", 0)
        booked_seats = ride.get("booked_seats", []) or []

        # Validations
        if total_seats <= 0:
            return Response({"error": "Ride has no seats configured"}, status=400)

        if seat_number < 1 or seat_number > total_seats:
            return Response({"error": "Invalid seat number"}, status=400)

        if seat_number in booked_seats:
            return Response({"error": f"Seat {seat_number} is already booked"}, status=400)

        # Create booking object stored in DB
        booking_doc = {
            "ride_id": str(ride["_id"]),
            "user_id": user_id,
            "email": email,
            "seat_number": seat_number,
            "price": int(ride.get("price", 0)),
            "status": "pending",
            "created_at": datetime.utcnow()
        }

        insert_result = bookings_collection.insert_one(booking_doc)
        booking_id = str(insert_result.inserted_id)

        # Update ride seat lists and counts
        trips_collection.update_one(
            {"_id": ride["_id"]},
            {
                "$push": {"booked_seats": seat_number},
                "$inc": {"available_seats": -1}
            }
        )

        # Return a normalized booking response frontend expects
        response = {
            "booking_id": booking_id,
            "seat_count": 1,
            "seat_number": seat_number,
            "total_price": int(ride.get("price", 0)),
            "status": "pending",
            "ride": {
                "origin": ride.get("origin"),
                "destination": ride.get("destination"),
                "departure_time": ride.get("departure_time"),
                "price": int(ride.get("price", 0))
            }
        }

        return Response(response, status=201)


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

        out = []
        for b in bookings:
            # convert ObjectId and include ride summary
            ride = None
            try:
                ride_doc = trips_collection.find_one({"_id": ObjectId(b.get("ride_id"))})
                if ride_doc:
                    ride = {
                        "origin": ride_doc.get("origin"),
                        "destination": ride_doc.get("destination"),
                        "departure_time": ride_doc.get("departure_time"),
                        "price": ride_doc.get("price")
                    }
            except Exception:
                ride = None

            out.append({
                "booking_id": str(b.get("_id")),
                "seat_number": b.get("seat_number"),
                "total_price": int(b.get("price", 0)),
                "status": b.get("status"),
                "ride": ride
            })

        return Response(out, status=200)


class BookingDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, booking_id):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except jwt.InvalidTokenError:
            return Response({"error": "Unauthorized"}, status=401)

        user_id = payload.get("user_id")

        booking = bookings_collection.find_one({"_id": ObjectId(booking_id), "user_id": user_id})
        if not booking:
            return Response({"error": "Booking not found"}, status=404)

        # attach ride summary
        ride = None
        try:
            ride_doc = trips_collection.find_one({"_id": ObjectId(booking.get("ride_id"))})
            if ride_doc:
                ride = {
                    "origin": ride_doc.get("origin"),
                    "destination": ride_doc.get("destination"),
                    "departure_time": ride_doc.get("departure_time"),
                    "price": ride_doc.get("price")
                }
        except Exception:
            ride = None

        response = {
            "booking_id": str(booking.get("_id")),
            "seat_count": 1,
            "seat_number": booking.get("seat_number"),
            "total_price": int(booking.get("price", 0)),
            "status": booking.get("status"),
            "ride": ride
        }

        return Response(response, status=200)


class MarkPaidView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, booking_id):
        result = bookings_collection.update_one({"_id": ObjectId(booking_id)}, {"$set": {"status": "paid"}})
        if result.matched_count == 0:
            return Response({"error": "Booking not found"}, status=404)
        return Response({"message": "Payment confirmed", "status": "paid"}, status=200)

# ===================== DASHBOARD: USER BOOKINGS =====================
class DashboardBookingsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Return bookings with ride summary (Dashboard)"""
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except jwt.InvalidTokenError:
            return Response({"error": "Unauthorized"}, status=401)

        user_id = payload.get("user_id")

        bookings = list(bookings_collection.find({"user_id": user_id}))
        output = []

        for b in bookings:
            ride_doc = trips_collection.find_one({"_id": ObjectId(b["ride_id"])})
            ride = {
                "from": ride_doc.get("origin"),
                "to": ride_doc.get("destination"),
                "date": ride_doc.get("departure_time"),
                "price": ride_doc.get("price")
            } if ride_doc else None

            output.append({
                "booking_id": str(b["_id"]),
                "seat_number": b.get("seat_number"),
                "amount": b.get("price"),
                "payment_status": b.get("status"),
                "ride": ride
            })

        return Response(output, status=200)



# ===================== DASHBOARD: USER PAYMENTS =====================
class DashboardPaymentsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Return list of payments for dashboard"""
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except jwt.InvalidTokenError:
            return Response({"error": "Unauthorized"}, status=401)

        user_id = payload.get("user_id")
        payments = list(payments_collection.find({"user_id": user_id}))

        for p in payments:
            p["_id"] = str(p["_id"])
            p["booking_id"] = str(p.get("booking_id", ""))

        return Response(payments, status=200)



# ===================== DASHBOARD: PENDING PAYMENTS =====================
class DashboardPendingPaymentsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Return pending payments only"""
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except jwt.InvalidTokenError:
            return Response({"error": "Unauthorized"}, status=401)

        user_id = payload.get("user_id")
        payments = list(payments_collection.find({"user_id": user_id, "status": "pending"}))

        for p in payments:
            p["_id"] = str(p["_id"])
            p["booking_id"] = str(p.get("booking_id", ""))

        return Response(payments, status=200)

@api_view(["POST"])
def verify_payment(request):
    data = request.data

    transaction_id = data.get("transaction_id")
    booking_id = data.get("booking_id")
    amount = data.get("amount")
    name = data.get("name")
    email = data.get("email")
    user_id = data.get("user_id")

    if not booking_id:
        return Response({"error": "booking_id is required"}, status=400)

    # 1️⃣ Save payment to database
    payments_collection.insert_one({
        "user_id": user_id,
        "booking_id": booking_id,
        "amount": amount,
        "status": "paid",
        "transaction_id": transaction_id,
        "created_at": datetime.utcnow()
    })

    # 2️⃣ Mark booking as paid
    bookings_collection.update_one(
        {"_id": ObjectId(booking_id)},
        {"$set": {"status": "paid"}}
    )

    # 3️⃣ Send Telegram alert
    message = f"""
💳 <b>New Payment Received!</b>
👤 <b>Name:</b> {name}
📧 <b>Email:</b> {email}
📦 <b>Booking ID:</b> {booking_id}
💰 <b>Amount:</b> ₦{amount}
🧾 <b>Transaction ID:</b> {transaction_id}
    """
    send_telegram_alert(message)

    return Response({"message": "Payment stored & verified."}, status=200)
