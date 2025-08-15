from rest_framework import generics, permissions
from .models import TravelPlan
from .serializers import TravelPlanSerializer
from rest_framework.response import Response
from rest_framework import status
from .models import Booking
from .serializers import BookingSerializer

# Driver can create and list their travel plans
class TravelPlanCreateView(generics.ListCreateAPIView):
    serializer_class = TravelPlanSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return TravelPlan.objects.filter(driver=self.request.user)

    def perform_create(self, serializer):
        serializer.save(driver=self.request.user)


# Public view - anyone can see available rides
class AvailableRidesListView(generics.ListAPIView):
    queryset = TravelPlan.objects.all().order_by("-created_at")
    serializer_class = TravelPlanSerializer
    permission_classes = [permissions.AllowAny]

# Passenger books a ride
class BookingCreateView(generics.CreateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(passenger=self.request.user)


# Passenger can see their bookings
class MyBookingsListView(generics.ListAPIView):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(passenger=self.request.user)


# Driver can see bookings for their trips
class DriverBookingsListView(generics.ListAPIView):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(travel_plan__driver=self.request.user)

from rest_framework.views import APIView

class BookingCancelView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, booking_id):
        try:
            booking = Booking.objects.get(id=booking_id, passenger=request.user)
        except Booking.DoesNotExist:
            return Response({"error": "Booking not found"}, status=status.HTTP_404_NOT_FOUND)

        # Restore seats
        booking.travel_plan.available_seats += booking.seats_booked
        booking.travel_plan.save()

        # Optional: refund logic (if payment integrated)
        # e.g., call Flutterwave/Stripe API to refund

        booking.delete()

        return Response({"message": "Booking cancelled and seats restored"}, status=status.HTTP_200_OK)
