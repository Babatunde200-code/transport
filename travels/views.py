from rest_framework import generics, permissions
from .models import TravelPlan, Booking
from .serializers import TravelPlanSerializer, BookingSerializer


# -------- Travel Plans --------
class TravelPlanListCreateView(generics.ListCreateAPIView):
    queryset = TravelPlan.objects.all().order_by("-created_at")
    serializer_class = TravelPlanSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(driver=self.request.user)


class TravelPlanDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = TravelPlan.objects.all()
    serializer_class = TravelPlanSerializer
    permission_classes = [permissions.IsAuthenticated]

class TravelPlanCreateView(generics.CreateAPIView):
    queryset = TravelPlan.objects.all()
    serializer_class = TravelPlanSerializer

# -------- Bookings --------
class BookingListCreateView(generics.ListCreateAPIView):
    queryset = Booking.objects.all().order_by("-created_at")
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(passenger=self.request.user)


class BookingDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
