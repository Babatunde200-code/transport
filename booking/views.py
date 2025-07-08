from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Booking
from travels.models import Travel
from .serializers import BookingSerializer
from rest_framework.decorators import api_view, permission_classes

class BookingListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        bookings = Booking.objects.filter(passenger=request.user)
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = BookingSerializer(data=request.data)
        if serializer.is_valid():
            travel = serializer.validated_data['travel']
            seats_requested = serializer.validated_data['seats_booked']

            if seats_requested > travel.available_seats:
                return Response({"detail": "Not enough available seats."}, status=400)

            travel.available_seats -= seats_requested
            travel.save()

            serializer.save(passenger=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

class BookingCancelView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            booking = Booking.objects.get(pk=pk, passenger=request.user)
        except Booking.DoesNotExist:
            return Response({"detail": "Not found."}, status=404)

        if booking.booking_status != 'cancelled':
            booking.booking_status = 'cancelled'
            booking.travel.available_seats += booking.seats_booked
            booking.travel.save()
            booking.save()

        return Response({"detail": "Booking cancelled."})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def driver_booking_list(request):
    travels = Travel.objects.filter(driver=request.user)
    bookings = Booking.objects.filter(travel__in=travels)
    serializer = BookingSerializer(bookings, many=True)
    return Response(serializer.data)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def approve_booking(request, pk):
    try:
        booking = Booking.objects.get(pk=pk, travel__driver=request.user)
    except Booking.DoesNotExist:
        return Response({'detail': 'Booking not found or unauthorized'}, status=404)

    booking.driver_status = 'approved'
    booking.save()
    serializer = BookingSerializer(booking)
    return Response(serializer.data)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def decline_booking(request, pk):
    try:
        booking = Booking.objects.get(pk=pk, travel__driver=request.user)
    except Booking.DoesNotExist:
        return Response({'detail': 'Booking not found or unauthorized'}, status=404)

    booking.driver_status = 'declined'
    booking.save()
    serializer = BookingSerializer(booking)
    return Response(serializer.data)
