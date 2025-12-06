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
from .models import Booking, Payment

SECRET_KEY = settings.SECRET_KEY


# ---------------- Helper ----------------
def _safe_object_id(val):
    """
    If val looks like an ObjectId string, return ObjectId(val).
    If it's already an ObjectId, return it.
    Otherwise return the original value (likely a string).
    """
    if val is None:
        return None
    if isinstance(val, ObjectId):
        return val
    try:
        return ObjectId(val)
    except Exception:
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

        try:
            ride_doc = trips_collection.find_one({"_id": ObjectId(ride_id)})
        except Exception:
            ride_doc = None

        if not ride_doc:
            return Response({"error": "Ride not found"}, status=404)

        try:
            total_seats = int(data.get("total_seats", ride_doc.get("total_seats", 0)))
        except (TypeError, ValueError):
            total_seats = ride_doc.get("total_seats", 0)

        booked = ride_doc.get("booked_seats", [])
        available = max(total_seats - len(booked), 0)

        update_data = {
            "origin": data.get("origin", ride_doc.get("origin")),
            "destination": data.get("destination", ride_doc.get("destination")),
            "departure_time": data.get("departure_time", ride_doc.get("departure_time")),
            "total_seats": total_seats,
            "available_seats": available,
            "price": int(data.get("price", ride_doc.get("price", 0))),
            "updated_at": datetime.utcnow()
        }

        trips_collection.update_one({"_id": ObjectId(ride_id)}, {"$set": update_data})
        return Response({"message": "Ride updated"}, status=200)

    def delete(self, request, ride_id):
        try:
            result = trips_collection.delete_one({"_id": ObjectId(ride_id)})
        except Exception:
            result = None

        if not result or result.deleted_count == 0:
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

        # Load ride (handle ride_id that might be string)
        try:
            ride_doc = trips_collection.find_one({"_id": _safe_object_id(ride_id)})
        except Exception:
            ride_doc = None

        if not ride_doc:
            return Response({"error": "Ride not found"}, status=404)

        total_seats = ride_doc.get("total_seats", 0)
        booked_seats = ride_doc.get("booked_seats", []) or []

        # Validations
        if total_seats <= 0:
            return Response({"error": "Ride has no seats configured"}, status=400)

        if seat_number < 1 or seat_number > total_seats:
            return Response({"error": "Invalid seat number"}, status=400)

        if seat_number in booked_seats:
            return Response({"error": f"Seat {seat_number} is already booked"}, status=400)

        # Create booking object stored in DB
        booking_doc = {
            "ride_id": str(ride_doc.get("_id")),
            "user_id": user_id,
            "email": email,
            "seat_number": seat_number,
            "price": int(ride_doc.get("price", 0)),
            "status": "pending",
            "created_at": datetime.utcnow()
        }

        insert_result = bookings_collection.insert_one(booking_doc)
        booking_id = str(insert_result.inserted_id)

        # Update ride seat lists and counts (push booked seat and decrement available)
        trips_collection.update_one(
            {"_id": _safe_object_id(ride_doc.get("_id"))},
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
            "total_price": int(ride_doc.get("price", 0)),
            "status": "pending",
            "ride": {
                "origin": ride_doc.get("origin"),
                "destination": ride_doc.get("destination"),
                "departure_time": ride_doc.get("departure_time"),
                "price": int(ride_doc.get("price", 0))
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
            ride = None
            try:
                ride_doc = trips_collection.find_one({"_id": _safe_object_id(b.get("ride_id"))})
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

        try:
            booking = bookings_collection.find_one({"_id": _safe_object_id(booking_id), "user_id": user_id})
        except Exception:
            booking = None

        if not booking:
            return Response({"error": "Booking not found"}, status=404)

        # attach ride summary
        ride = None
        try:
            ride_doc = trips_collection.find_one({"_id": _safe_object_id(booking.get("ride_id"))})
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
        try:
            result = bookings_collection.update_one({"_id": _safe_object_id(booking_id)}, {"$set": {"status": "paid"}})
        except Exception:
            result = None

        if not result or result.matched_count == 0:
            return Response({"error": "Booking not found"}, status=404)
        return Response({"message": "Payment confirmed", "status": "paid"}, status=200)


# ===================== DASHBOARD: SUMMARY =====================
class DashboardSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except jwt.InvalidTokenError:
            return Response({"error": "Unauthorized"}, status=401)

        user_id = payload.get("user_id")

        total_trips = bookings_collection.count_documents({"user_id": user_id})

        # sum paid payments
        total_payments = 0.0
        try:
            for p in payments_collection.find({"user_id": user_id, "status": "paid"}):
                try:
                    total_payments += float(p.get("amount", 0) or 0)
                except Exception:
                    pass
        except Exception:
            total_payments = 0.0

        pending_count = payments_collection.count_documents({"user_id": user_id, "status": "pending"})

        travel_history_count = total_trips

        return Response({
            "total_trips": total_trips,
            "total_payments": total_payments,
            "pending_payments": pending_count,
            "travel_history_count": travel_history_count
        }, status=200)


# ===================== DASHBOARD: USER BOOKINGS =====================
class DashboardBookingsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Return recent bookings for THIS USER or ALL (if admin)."""

        user = request.user

        if user.is_staff:
            # Admin sees all bookings
            bookings = Booking.objects.all().order_by("-created_at")[:20]
        else:
            # Normal user sees only their own
            bookings = Booking.objects.filter(user_id=user.id).order_by("-created_at")[:20]

        serialized = [
            {
                "origin": b.origin,
                "destination": b.destination,
                "date": b.created_at.strftime("%Y-%m-%d"),
                "amount": b.amount,
                "payment_status": b.payment_status,
            }
            for b in bookings
        ]

        return Response({
            "recent_bookings": serialized
        }, status=200)



# ==========================================================
# ✅ DASHBOARD — TOTAL PAYMENTS (sum)
# ==========================================================
class DashboardPaymentsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Return the TOTAL amount paid by this user or all users if admin."""

        user = request.user

        if user.is_staff:
            payments = Payment.objects.filter(status="paid")
        else:
            payments = Payment.objects.filter(user_id=user.id, status="paid")

        total = sum([p.amount for p in payments])

        return Response({
            "total_payments": total
        }, status=200)



# ==========================================================
# ✅ DASHBOARD — PENDING PAYMENTS (count)
# ==========================================================
class DashboardPendingPaymentsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Return the number of unpaid or pending payments."""

        user = request.user

        if user.is_staff:
            pending = Payment.objects.filter(status__in=["pending", "unpaid"])
        else:
            pending = Payment.objects.filter(
                user_id=user.id,
                status__in=["pending", "unpaid"]
            )

        return Response({
            "pending_payments": pending.count()
        }, status=200)

# ------------------- PAYMENT WEBHOOK / VERIFICATION -------------------
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

    # try to get user_id from booking if not supplied
    try:
        stored_booking = bookings_collection.find_one({"_id": _safe_object_id(booking_id)})
        if stored_booking and not user_id:
            user_id = stored_booking.get("user_id")
    except Exception:
        stored_booking = None

    # store payment (use safe conversions)
    try:
        payments_collection.insert_one({
            "user_id": user_id,
            "booking_id": booking_id,
            "amount": float(amount or 0),
            "status": "paid",
            "transaction_id": transaction_id,
            "created_at": datetime.utcnow()
        })
    except Exception:
        # fallback: store with raw amount
        payments_collection.insert_one({
            "user_id": user_id,
            "booking_id": booking_id,
            "amount": amount,
            "status": "paid",
            "transaction_id": transaction_id,
            "created_at": datetime.utcnow()
        })

    # mark booking as paid if possible
    try:
        bookings_collection.update_one(
            {"_id": _safe_object_id(booking_id)},
            {"$set": {"status": "paid"}}
        )
    except Exception:
        pass

    # send telegram alert (best-effort)
    try:
        message = f"""
💳 <b>New Payment Received!</b>
👤 <b>Name:</b> {name}
📧 <b>Email:</b> {email}
📦 <b>Booking ID:</b> {booking_id}
💰 <b>Amount:</b> ₦{amount}
🧾 <b>Transaction ID:</b> {transaction_id}
"""
        send_telegram_alert(message)
    except Exception:
        pass

    return Response({"message": "Payment stored & verified."}, status=200)
