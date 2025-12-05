from django.urls import path
from . import views
from .views import (
    AdminSignupView,
    AdminLoginView,
    AdminRideView,
    RideListView,
    BookRideView,
    UserBookingsView,
    BookingDetailView,
    MarkPaidView,
    DashboardBookingsView,
    DashboardPaymentsView,
    DashboardPendingPaymentsView
)

urlpatterns = [
    # admin ride management
    path("admin/signup/", AdminSignupView.as_view(), name="admin-signup"),
    path("admin/login/", AdminLoginView.as_view(), name="admin-login"),
    path("admin/rides/", AdminRideView.as_view(), name="admin-ride-create"),
    path("admin/rides/<str:ride_id>/", AdminRideView.as_view(), name="admin-ride-update-delete"),

    # user rides
    path("rides/", RideListView.as_view(), name="ride-list"),
    path("rides/<str:ride_id>/book/", BookRideView.as_view(), name="book-ride"),
    path("bookings/", UserBookingsView.as_view(), name="user-bookings"),
    path("bookings/<str:booking_id>/", BookingDetailView.as_view(), name="booking-detail"),  # ✅ new
    path("bookings/<str:booking_id>/pay/", MarkPaidView.as_view(), name="mark-paid"),
    path("verify-payment/", views.verify_payment, name="verify-payment"),
    path("bookings", DashboardBookingsView.as_view()),
    path("payments", DashboardPaymentsView.as_view()),
    path("payments/pending", DashboardPendingPaymentsView.as_view()),
]
