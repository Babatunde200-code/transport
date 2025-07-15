from rest_framework import generics, permissions
from .models import Booking
from .serializers import BookingSerializer
from django.core.mail import send_mail
from django.conf import settings

class BookingCreateView(generics.CreateAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        booking = serializer.save(user=self.request.user)
        self.send_confirmation_email(booking)

    def send_confirmation_email(self, booking):
        subject = 'Booking Confirmation'
        message = (
            f"Hi {booking.user.first_name},\n\n"
            f"Your booking from {booking.origin} to {booking.destination} "
            f"on {booking.travel_date} has been received.\n\n"
            f"Thank you for using our service!"
        )
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [booking.user.email])
