from django.urls import path
from .views import (
    TravelPlanCreateView,
    TravelPlanListCreateView,
   TravelPlanDetailView,
    BookingListCreateView,
    BookingDetailView,
)

urlpatterns = [
    path("travel-plans/", TravelPlanCreateView.as_view(), name="travel-plans"),
    path("available-rides/", TravelPlanListCreateView.as_view(), name="available-rides"),
    path("book-ride/", TravelPlanDetailView.as_view(), name="book-ride"),
    path("my-bookings/", BookingListCreateView.as_view(), name="my-bookings"),
    path("cancel-booking/<int:booking_id>/", BookingDetailView.as_view(), name="cancel-booking"),
]
