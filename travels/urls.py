from django.urls import path
from .views import (
    TravelPlanCreateView,
    AvailableRidesListView,
    BookingCreateView,
    MyBookingsListView,
    DriverBookingsListView,
    BookingCancelView,
)

urlpatterns = [
    path("travel-plans/", TravelPlanCreateView.as_view(), name="travel-plans"),
    path("available-rides/", AvailableRidesListView.as_view(), name="available-rides"),
    path("book-ride/", BookingCreateView.as_view(), name="book-ride"),
    path("my-bookings/", MyBookingsListView.as_view(), name="my-bookings"),
    path("driver-bookings/", DriverBookingsListView.as_view(), name="driver-bookings"),
    path("cancel-booking/<int:booking_id>/", BookingCancelView.as_view(), name="cancel-booking"),
]
