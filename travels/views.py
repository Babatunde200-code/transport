from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView
from .models import TravelPlan
from .serializers import TravelPlanSerializer
from datetime import date
from rest_framework import generics
from travels.models import Booking
from .serializers import BookingSerializer


# travels/views.py

class TravelPlanView(generics.ListCreateAPIView):
    queryset = TravelPlan.objects.all()
    serializer_class = TravelPlanSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(driver=self.request.user)

class BookingView(generics.CreateAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        booking = serializer.save(user=self.request.user)
        send_mail(
            subject='New Booking Request',
            message='Visit your dashboard to accept/reject.',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[booking.plan.driver.email]
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def accept_booking(request, pk):
    booking = Booking.objects.get(pk=pk, plan__driver=request.user)
    booking.status = 'accepted'
    booking.save()
    send_mail(
        subject='Booking Accepted',
        message=f'Pay for your ride: http://localhost:3000/payment/{booking.id}',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[booking.user.email]
    )
    return Response({'message': 'Booking accepted.'})

