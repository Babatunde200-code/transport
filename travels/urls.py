from django.urls import path
from .views import TravelPlanView, BookingView, accept_booking

# travels/urls.py

urlpatterns = [
    path('plans/', TravelPlanView.as_view()),
    path('bookings/', BookingView.as_view()),
    path('bookings/<int:pk>/accept/', accept_booking),
]

